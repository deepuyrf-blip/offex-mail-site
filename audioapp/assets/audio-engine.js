/* ==========================================================================
   Offex Audio — in-browser audio engine (no server required)
   Removes silence and cleans voice entirely inside the browser using the
   Web Audio API. Exposes window.OffexEngine with Promise-returning helpers
   that resolve to a WAV Blob.
   ========================================================================== */
(function () {
  "use strict";

  function floatToWavBlob(buf) {
    var nCh = buf.numberOfChannels, len = buf.length * nCh * 2 + 44;
    var ab = new ArrayBuffer(len), v = new DataView(ab);
    var ws = function (o, s) { for (var i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
    ws(0, "RIFF"); v.setUint32(4, 36 + buf.length * nCh * 2, true); ws(8, "WAVE"); ws(12, "fmt ");
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, nCh, true);
    v.setUint32(24, buf.sampleRate, true); v.setUint32(28, buf.sampleRate * nCh * 2, true);
    v.setUint16(32, nCh * 2, true); v.setUint16(34, 16, true);
    ws(36, "data"); v.setUint32(40, buf.length * nCh * 2, true);
    var chs = [];
    for (var c = 0; c < nCh; c++) chs.push(buf.getChannelData(c));
    var off = 44;
    for (var i = 0; i < buf.length; i++) {
      for (var c2 = 0; c2 < nCh; c2++) {
        var s = Math.max(-1, Math.min(1, chs[c2][i]));
        v.setInt16(off, s < 0 ? s * 32768 : s * 32767, true); off += 2;
      }
    }
    return new Blob([ab], { type: "audio/wav" });
  }

  function decode(file) {
    return new Promise(function (resolve, reject) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { reject(new Error("Web Audio is not supported in this browser.")); return; }
      var ac = new AC();
      var done = function (buf) { try { ac.close(); } catch (e) {} resolve(buf); };
      var fail = function (e) { try { ac.close(); } catch (e2) {} reject(e || new Error("Could not decode this audio file.")); };
      file.arrayBuffer().then(function (ab) {
        var p = ac.decodeAudioData(ab, done, fail);
        if (p && typeof p.then === "function") p.then(done, fail);
      }).catch(fail);
    });
  }

  function rmsEnvelope(chans, len, nch, hop) {
    var frames = Math.ceil(len / hop), rms = new Float32Array(frames);
    for (var f = 0; f < frames; f++) {
      var a = f * hop, b = Math.min(len, a + hop), sum = 0, n = 0;
      for (var c = 0; c < nch; c++) {
        var d = chans[c];
        for (var j = a; j < b; j += 2) { var q = d[j]; sum += q * q; n++; }
      }
      rms[f] = n ? Math.sqrt(sum / n) : 0;
    }
    return rms;
  }

  function percentile(arr, p) {
    var s = Float32Array.from(arr).sort();
    var i = Math.min(s.length - 1, Math.max(0, Math.floor(s.length * p)));
    return s[i] || 0;
  }

  /* ---- Remove silence: keep up to `keepSec` of every pause ---- */
  async function removeSilence(file, keepSec) {
    keepSec = Math.max(0, Number(keepSec) || 0);
    var buf = await decode(file);
    var sr = buf.sampleRate, nch = buf.numberOfChannels, len = buf.length;
    var chans = []; for (var c = 0; c < nch; c++) chans.push(buf.getChannelData(c));

    var hop = Math.max(64, Math.round(sr * 0.02));
    var rms = rmsEnvelope(chans, len, nch, hop), frames = rms.length;
    var ref = percentile(rms, 0.98) || 0.1;
    var thr = Math.max(0.002, Math.min(0.02, ref * 0.09));
    var fdur = hop / sr, minFr = Math.ceil(0.20 / fdur);

    var keep = new Uint8Array(frames).fill(1);
    var st = -1;
    for (var f = 0; f <= frames; f++) {
      var quiet = f < frames && rms[f] < thr;
      if (quiet) { if (st < 0) st = f; }
      else if (st >= 0) {
        if (f - st >= minFr) {
          var keepFr = Math.round(keepSec / fdur);
          for (var k = st + keepFr; k < f; k++) keep[k] = 0;
        }
        st = -1;
      }
    }

    var keptFrames = 0;
    for (var i2 = 0; i2 < frames; i2++) if (keep[i2]) keptFrames++;
    if (!keptFrames) throw new Error("No audio content detected — the file looks silent.");

    var outLen = keptFrames * hop;
    var OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    var octx = new OAC(nch, outLen, sr);
    var out = octx.createBuffer(nch, outLen, sr);
    var w = 0, fadeN = Math.min(hop, Math.round(sr * 0.004));
    for (var f2 = 0; f2 < frames; f2++) {
      if (!keep[f2]) continue;
      var a2 = f2 * hop, b2 = Math.min(len, a2 + hop), n2 = b2 - a2;
      var prevKept = f2 > 0 && keep[f2 - 1], nextKept = f2 + 1 < frames && keep[f2 + 1];
      for (var c3 = 0; c3 < nch; c3++) {
        var src = chans[c3], dst = out.getChannelData(c3), seg = src.subarray(a2, b2);
        dst.set(seg, w);
        if (!prevKept) for (var z = 0; z < fadeN && z < n2; z++) dst[w + z] *= z / fadeN;
        if (!nextKept) for (var z2 = 0; z2 < fadeN && z2 < n2; z2++) dst[w + n2 - 1 - z2] *= z2 / fadeN;
      }
      w += n2;
    }
    return { blob: floatToWavBlob(out), duration: out.duration, removed: Math.max(0, buf.duration - out.duration) };
  }

  /* ---- Enhance voice: high-pass + adaptive noise gate + peak normalize ---- */
  async function enhance(file, mode) {
    var cfg = { "Light": { hp: 70, sens: 1.5, floor: 0.55 }, "Balanced": { hp: 90, sens: 2.2, floor: 0.42 }, "Strong": { hp: 120, sens: 3.2, floor: 0.30 } }[mode] || { hp: 90, sens: 2.2, floor: 0.42 };
    var buf = await decode(file);
    var sr = buf.sampleRate, nch = buf.numberOfChannels, len = buf.length;
    var OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    var octx = new OAC(nch, len, sr);
    var out = octx.createBuffer(nch, len, sr);

    // High-pass filter coefficients (one-pole)
    var rc = 1 / (2 * Math.PI * cfg.hp), dt = 1 / sr, alpha = rc / (rc + dt);

    var peak = 0;
    for (var c = 0; c < nch; c++) {
      var src = buf.getChannelData(c), dst = out.getChannelData(c);
      // 1) high-pass to strip rumble
      var prevIn = 0, prevOut = 0;
      for (var i = 0; i < len; i++) { var x = src[i]; var y = alpha * (prevOut + x - prevIn); prevIn = x; prevOut = y; dst[i] = y; }

      // 2) adaptive gate using a coarse envelope
      var win = Math.max(1, Math.round(sr * 0.012)), wc = Math.ceil(len / win);
      var env = new Float32Array(wc);
      for (var wI = 0; wI < wc; wI++) {
        var a = wI * win, b = Math.min(len, a + win), s = 0, n = 0;
        for (var j = a; j < b; j++) { s += dst[j] * dst[j]; n++; }
        env[wI] = n ? Math.sqrt(s / n) : 0;
      }
      var floorN = percentile(env, 0.15) || 0;
      var thr = Math.max(floorN * (1 + cfg.sens * 2), cfg.floor * 0.006);
      // gain per window with soft knee, then smooth
      var gain = new Float32Array(wc);
      for (var g = 0; g < wc; g++) {
        var v = env[g];
        gain[g] = v >= thr ? 1 : Math.max(0.06, Math.pow(v / thr, 1.6));
      }
      for (var sm = 1; sm < wc - 1; sm++) gain[sm] = (gain[sm - 1] + gain[sm] * 2 + gain[sm + 1]) / 4;
      for (var i2 = 0; i2 < len; i2++) {
        var wI2 = (i2 / win) | 0;
        var gi = Math.min(wc - 1, wI2), gnext = Math.min(wc - 1, gi + 1);
        var frac = i2 / win - wI2, gv = gain[gi] * (1 - frac) + gain[gnext] * frac;
        dst[i2] *= gv;
      }
      // 3) peak measurement for normalization
      for (var i3 = 0; i3 < len; i3++) { var av = Math.abs(dst[i3]); if (av > peak) peak = av; }
    }
    // normalize toward -1 dBFS (peak ~0.89) only if quiet enough to benefit
    if (peak > 0.001) {
      var scale = Math.min(2.4, 0.89 / peak);
      if (scale > 1.001) {
        for (var c4 = 0; c4 < nch; c4++) { var d = out.getChannelData(c4); for (var i4 = 0; i4 < len; i4++) d[i4] = Math.max(-1, Math.min(1, d[i4] * scale)); }
      }
    }
    return { blob: floatToWavBlob(out), duration: out.duration, mode: mode };
  }

  window.OffexEngine = {
    supported: !!(window.AudioContext || window.webkitAudioContext),
    removeSilence: removeSilence,
    enhance: enhance,
    toWavBlob: floatToWavBlob
  };
})();

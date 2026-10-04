import os

from huggingface_hub import HfApi

api = HfApi(token=os.environ["HF_TOKEN"])
RID = "factblink514/Compiled"

NEW = "offexmail.online,offex.cyou,11lab.bond"

try:
    print("BEFORE:", api.get_space_variables(RID))
except Exception as e:
    print("BEFORE err:", e)

try:
    api.add_space_variable(RID, key="DOMAINS", value=NEW)
    print("SET ok:", NEW)
except Exception as e:
    print("SET err:", e)

try:
    print("AFTER:", api.get_space_variables(RID))
except Exception as e:
    print("AFTER err:", e)

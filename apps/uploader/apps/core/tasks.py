import logging
import random
import shutil

import requests
from core.settings import c_app, STORE_PATH, NOTIFY_SERVICE, NOTIFY_SERVICE_ERROR


@c_app.task
def save_file_send_to_decomposer_service(file_path, filename, user_id):
    full_path = "{root_store}/{rand}_{filename}".format(root_store=STORE_PATH,
                                                        rand=str(random.random())[2:],
                                                        filename=filename)
    logging.debug("save file from {} to {}".format(file_path, full_path))
    try:
        shutil.copyfile(file_path, full_path)
    except Exception as e:
        requests.post(NOTIFY_SERVICE_ERROR, {"error": str(e)})
        return {"error": str(e)}

    r = requests.post(NOTIFY_SERVICE,
                      {'file_path': full_path, "filename": filename, "user_id": user_id})
    logging.debug("response, {}".format(r.text))
    return r.text


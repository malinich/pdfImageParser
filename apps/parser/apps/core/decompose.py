import logging
import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

from wand.image import Image


class Decomposer:
    def __init__(self, publish_service, store_path):
        self.store_path = store_path
        self.publish_service = publish_service

    async def decompose_pdf_onto_images(self, file_path,
                                        filename, user_id, resolution=150):
        pdf_component = {"file_path": file_path,
                         "filename": filename,
                         "images": [],
                         "user_id": user_id}
        all_pages = Image(filename=file_path, resolution=resolution)
        func = partial(self.parse_pdf_sequence, file_path)
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = (pool.submit(func, idx, page)
                       for idx, page in enumerate(all_pages.sequence))
            for f in as_completed(futures):
                try:
                    res = f.result()
                    pdf_component["images"].append(res)
                except Exception as e:
                    print(e)
                    logging.error(e)

        await self.publish_service.publish(pdf_component)

    def parse_pdf_sequence(self, filename, index, page):
        with Image(page) as img:
            img.format = 'png'
            image_filename = os.path.splitext(os.path.basename(filename))[0]
            image_filename = os.path.join(self.store_path,
                                          '{}-{}.png'.format(image_filename, index))
            img.save(filename=image_filename)
            return image_filename

import threading

from run_zone import run_zone_camera
from run_entry import run_entry_camera
from run_billing import run_billing_camera


threads = [

    threading.Thread(
        target=run_zone_camera,
        args=("STORE1_CAM1",)
    ),

    threading.Thread(
        target=run_zone_camera,
        args=("STORE1_CAM2",)
    ),

    # threading.Thread(
    #     target=run_entry_camera,
    #     args=("STORE1_CAM3",)
    # ),

    # threading.Thread(
    #     target=run_billing_camera,
    #     args=("STORE1_CAM5",)
    # ),

    # threading.Thread(
    #     target=run_entry_camera,
    #     args=("STORE2_ENTRY1",)
    # ),

    threading.Thread(
        target=run_entry_camera,
        args=("STORE2_ENTRY2",)
    ),

    # threading.Thread(
    #     target=run_zone_camera,
    #     args=("STORE2_CAM1",)
    # ),

    threading.Thread(
        target=run_billing_camera,
        args=("STORE2_CAM5",)
    )

]


for t in threads:
    t.start()

for t in threads:
    t.join()
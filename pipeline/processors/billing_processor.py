class BillingProcessor:

    def __init__(self):

        self.queue_entry_frame = {}

        self.purchase_done = set()

        self.queue_entered = set()

        self.last_queue_depth = -1

    
    def has_entered_queue(
        self,
        track_id
    ):

        return (
            track_id
            in
            self.queue_entered
        )


    def mark_queue_entered(
        self,
        track_id
    ):

        self.queue_entered.add(
            track_id
        )

    def purchase_completed(
        self,
        track_id
    ):

        return (
            track_id
            in
            self.purchase_done
        )


    def mark_purchase_completed(
        self,
        track_id
    ):

        self.purchase_done.add(
            track_id
        )


    def set_queue_entry_frame(
        self,
        track_id,
        frame_number
    ):

        self.queue_entry_frame[
            track_id
        ] = frame_number


    def get_queue_entry_frame(
        self,
        track_id
    ):

        return self.queue_entry_frame.get(
            track_id
        )
    
    def clear_queue_entry_frame(
        self,
        track_id
    ):

        if track_id in self.queue_entry_frame:

            del self.queue_entry_frame[
                track_id
            ]
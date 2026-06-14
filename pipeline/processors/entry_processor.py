class EntryProcessor:

    def __init__(self, entry_line_y):
        self.entry_line_y = entry_line_y
        self.entered = set()
        self.previous_y = {}

    def update_position(
        self,
        track_id,
        foot_y
    ):

        if track_id not in self.previous_y:
            self.previous_y[track_id] = foot_y

        old_y = self.previous_y[track_id]

        self.previous_y[track_id] = foot_y

        return old_y
    
    def check_crossing(
        self,
        track_id,
        old_y,
        foot_y
    ):

        if (
            old_y < self.entry_line_y
            and foot_y > self.entry_line_y
            and track_id not in self.entered
        ):

            self.entered.add(track_id)

            return "STORE_ENTER"

        elif (
            old_y > self.entry_line_y
            and foot_y < self.entry_line_y
            and track_id in self.entered
        ):

            self.entered.remove(track_id)

            return "STORE_EXIT"

        return None
    
    def has_entered(
        self,
        track_id
    ):
        return track_id in self.entered
    
    
    def should_ignore(
        self,
        staff_flag
    ):
        return staff_flag
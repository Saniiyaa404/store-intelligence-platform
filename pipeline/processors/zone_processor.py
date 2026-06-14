class ZoneProcessor:

    def __init__(
        self,
        confirmation_frames
    ):

        self.confirmation_frames = confirmation_frames

        self.entry_frame = {}
        self.visitor_current_zone = {}
        self.pending_exit = {}

        self.last_zone = {}
        self.session_seq = {}

        self.zone_candidate = {}
        self.zone_candidate_count = {}

    def get_current_zone(
        self,
        track_id
    ):

        if track_id not in self.visitor_current_zone:
            self.visitor_current_zone[track_id] = None

        return self.visitor_current_zone[track_id]
    
    def set_current_zone(
        self,
        track_id,
        zone
    ):

        self.visitor_current_zone[track_id] = zone

    def update_zone_candidate(
        self,
        track_id,
        zone
    ):

        if zone is None:
            return

        if track_id not in self.zone_candidate:

            self.zone_candidate[track_id] = zone
            self.zone_candidate_count[track_id] = 1

        elif self.zone_candidate[track_id] == zone:

            self.zone_candidate_count[track_id] += 1

        else:

            self.zone_candidate[track_id] = zone
            self.zone_candidate_count[track_id] = 1

    def is_zone_confirmed(
        self,
        track_id
    ):

        return (
            self.zone_candidate_count.get(
                track_id,
                0
            )
            >=
            self.confirmation_frames
        )
    
    def get_session_seq(
        self,
        track_id
    ):

        if track_id not in self.session_seq:
            self.session_seq[track_id] = 1

        return self.session_seq[track_id]
    
    
    def increment_session_seq(
        self,
        track_id
    ):

        if track_id not in self.session_seq:
            self.session_seq[track_id] = 1

        self.session_seq[track_id] += 1

    #temp addition
    def reset_zone_candidate(
        self,
        track_id
    ):

        self.zone_candidate_count[track_id] = 0


    def start_zone_visit(
        self,
        track_id,
        zone,
        frame_number
    ):

        self.entry_frame[track_id] = frame_number

        self.set_current_zone(
            track_id,
            zone
        )

        self.last_zone[track_id] = zone

    
    def get_last_zone(
        self,
        track_id
    ):

        return self.last_zone.get(
            track_id
        )
    
    
    def get_entry_frame(
        self,
        track_id,
        default_frame
    ):

        return self.entry_frame.get(
            track_id,
            default_frame
        )
    
    
    def clear_zone_visit(
        self,
        track_id
    ):

        self.set_current_zone(
            track_id,
            None
        )

        if track_id in self.entry_frame:
            del self.entry_frame[track_id]

    
    def mark_pending_exit(
        self,
        track_id,
        frame_number
    ):
        self.pending_exit[track_id] = frame_number

    
    def is_pending_exit(
        self,
        track_id
    ):
        return track_id in self.pending_exit
    

    def get_pending_exit_frame(
        self,
        track_id
    ):
        return self.pending_exit.get(
            track_id
        )
    

    def clear_pending_exit(
        self,
        track_id
    ):
        if track_id in self.pending_exit:
            del self.pending_exit[track_id]
            

    
    def get_pending_exit_tracks(
        self
    ):
        return list(
            self.pending_exit.keys()
        )
import uuid

REENTRY_WINDOW_SECONDS = 240

class IdentityManager:

    def __init__(self):

        self.track_to_visitor = {}

        self.active_visitors = {}

        self.recently_exited = {}

    def create_visitor_id(self):

        return (
            "VIS_" +
            str(uuid.uuid4())[:8]
        )
    

    def assign_track(
        self,
        camera_id,
        track_id,
        visitor_id
    ):

        self.track_to_visitor[
            (camera_id, track_id)
        ] = visitor_id

    
    def get_visitor_for_track(
        self,
        camera_id,
        track_id
    ):

        return self.track_to_visitor.get(
            (camera_id, track_id)
        )
    

    def add_active_visitor(
        self,
        visitor_id,
        embedding,
        timestamp,
        osnet_embedding=None
    ):

        self.active_visitors[
            visitor_id
        ] = {

            "embedding": embedding,

            "osnet_embedding":
            osnet_embedding,

            "last_seen": timestamp,

            "tracks": set()
        }

    
    def visitor_exists(
        self,
        visitor_id
    ):

        return (
            visitor_id
            in
            self.active_visitors
        )
    

    def update_last_seen(
        self,
        visitor_id,
        timestamp
    ):

        if visitor_id in self.active_visitors:

            self.active_visitors[
                visitor_id
            ]["last_seen"] = timestamp


    def add_track_to_visitor(
        self,
        visitor_id,
        camera_id,
        track_id
    ):

        if visitor_id not in self.active_visitors:
            return

        self.active_visitors[
            visitor_id
        ]["tracks"].add(
            (camera_id, track_id)
        )

    
    def move_to_recently_exited(
        self,
        visitor_id,
        embedding,
        timestamp
    ):

        self.recently_exited[
            visitor_id
        ] = {

            "embedding": embedding,

            "exit_time": timestamp
        }

        if visitor_id in self.active_visitors:

            del self.active_visitors[
                visitor_id
            ]

    
    def get_recently_exited(self):

        return self.recently_exited
    

    def cleanup_expired_reentries(
        self,
        current_time
    ):

        expired = []

        for visitor_id, data in (
            self.recently_exited.items()
        ):

            gap = (
                current_time -
                data["exit_time"]
            ).total_seconds()

            if gap > REENTRY_WINDOW_SECONDS:

                expired.append(
                    visitor_id
                )

        for visitor_id in expired:

            del self.recently_exited[
                visitor_id
            ]

    def get_visitor_embedding(
        self,
        visitor_id
    ):

        if visitor_id not in self.active_visitors:
            return None

        return self.active_visitors[
            visitor_id
        ]["embedding"]
    

    def update_active_visitor(
        self,
        visitor_id,
        embedding,
        timestamp,
        osnet_embedding=None
    ):

        if visitor_id not in self.active_visitors:

            self.add_active_visitor(
                visitor_id,
                embedding,
                timestamp,
                osnet_embedding
            )

            return

        self.active_visitors[
            visitor_id
        ]["embedding"] = embedding

        self.update_visitor_embedding(
            visitor_id,
            embedding
        )

        self.update_osnet_embedding(
            visitor_id,
            osnet_embedding
        )

        self.update_last_seen(
            visitor_id,
            timestamp
        )
        

    def get_active_visitors(self):

        return self.active_visitors
    

    def get_track_mapping(self):

        return self.track_to_visitor
    
    
    def get_last_seen(
        self,
        visitor_id
    ):

        if visitor_id not in self.active_visitors:
            return None

        return self.active_visitors[
            visitor_id
        ]["last_seen"]
    

    def get_visitor_data(
        self,
        visitor_id
    ):

        return self.active_visitors.get(
            visitor_id
        )
    

    def update_visitor_embedding(
        self,
        visitor_id,
        embedding
    ):

        if visitor_id not in self.active_visitors:
            return

        self.active_visitors[
            visitor_id
        ]["embedding"] = embedding

    def update_osnet_embedding(
        self,
        visitor_id,
        osnet_embedding
    ):

        if visitor_id not in self.active_visitors:
            return

        self.active_visitors[
            visitor_id
        ]["osnet_embedding"] = (
            osnet_embedding
        )

identity_manager = IdentityManager()
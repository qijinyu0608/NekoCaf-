class ReservationStateError(ValueError):
    def __init__(self, current_status: str):
        super().__init__(current_status)
        self.current_status = current_status


class StoreUnavailableError(ValueError):
    pass


class InvalidReservationRequestError(ValueError):
    pass

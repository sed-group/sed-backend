from fastapi import HTTPException, Request, status


class MeasurementAccessChecker:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):

        # TODO: Lookup measurement set ID. Is it mapped to a project? Does the user have access to that project?

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access to measurement is restricted."
        )

from fastapi import HTTPException, status

#### HELPER FUNCTIONS 
def not_yet_implemented():
    ''' 
    dummy function for not yet implemented API functions 
    '''
    raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="API point has not been realised yet, we appologize"
        )

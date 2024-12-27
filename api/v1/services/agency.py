from sqlalchemy.orm import Session

from api.v1.models.emergency import Emergency
from api.v1.models.agency import Agency
from api.v1.models.responder import Responder
from api.v1.models.responder_emergency import ResponderEmergency


class AgencyService:
    
    @classmethod
    def get_agency_full_details(cls, db: Session, current_user):
        '''Fetch agency details and associated emergencies'''
        
        agency = Agency.fetch_one_by_field(db, creator_id=current_user.id)

        emergencies = (
            db.query(Emergency)
            .join(ResponderEmergency, Emergency.id == ResponderEmergency.emergency_id)
            .join(Responder, Responder.id == ResponderEmergency.responder_id)
            .join(Agency, Agency.id == Responder.agency_id)
            .filter(Agency.id == agency.id)
            .all()
        )
        print(emergencies)
        
        data = {
            'user': current_user,
            'agency': agency,
            'emergencies': emergencies,
            'responders': agency.responders,
            'resources': agency.resources,
        }
        
        return data

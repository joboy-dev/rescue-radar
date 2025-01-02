from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.v1.models.emergency import EVENT_TYPE_EMOJIS, Emergency
from api.v1.models.agency import Agency
from api.v1.models.responder import Responder
from api.v1.models.responder_emergency import ResponderEmergency


class AgencyService:
    
    @classmethod
    def get_agency_full_details(cls, db: Session, current_user):
        '''Fetch agency details and associated emergencies'''
        
        # Get the current date and calculate the start and end of the current year
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        # Calculate the start and end of the year
        start_of_year = datetime(now.year, 1, 1)
        end_of_year = datetime(now.year, 12, 31)
        
        agency = Agency.fetch_one_by_field(db, creator_id=current_user.id)

        # Get agency emergencies with associated responders and agencies
        query = (
            db.query(Emergency)
            .join(ResponderEmergency, Emergency.id == ResponderEmergency.emergency_id)
            .join(Responder, Responder.id == ResponderEmergency.responder_id)
            .join(Agency, Agency.id == Responder.agency_id)
            .filter(Agency.id == agency.id)
            .order_by(Emergency.created_at.asc())
            .order_by(Emergency.severity.desc())
        )
        agency_emergencies = query.all()
        active_emergencies = query.filter(Emergency.status == 'In Progress').all()
        agency_emergency_count = query.count()
        
        # Get all emergencies
        all_emergencies = Emergency.all(db)
        all_pending_emergencies = Emergency.fetch_by_field(db, order='asc' ,status='Pending')
        
        # Get total agency emergencies completed this month
        completed_emergencies_this_month = (
            query
            .filter(Emergency.status == 'Resolved')
            .filter(Emergency.updated_at.between(start_of_month, end_of_month))
            .count()
        )
        
        # Get total agency emergencies completed in the past year
        completed_emergencies_this_year = (
            query
            .filter(Emergency.status == 'Resolved')
            .filter(Emergency.updated_at.between(start_of_year, end_of_year))
            .count()
        )
        
        # Get total agency emergencies completed this month
        total_emergencies_this_month = (
            query
            .filter(Emergency.created_at.between(start_of_month, end_of_month))
            .count()
        )
        
        # Get total agency emergencies completed in the past year
        total_emergencies_this_year = (
            query
            .filter(Emergency.created_at.between(start_of_year, end_of_year))
            .count()
        )
        
        # Get available responders
        available_responders = Responder.fetch_by_field(
            db, 
            agency_id=agency.id,
            status='available',
        )
        
        # Get active responders
        engaged_responders = Responder.fetch_by_field(
            db, 
            agency_id=agency.id,
            status='engaged',
        )
        
        data = {
            'user': current_user,
            'agency': agency,
            'emergencies': all_pending_emergencies,
            'active_emergencies': active_emergencies,
            'active_emergencies_count': len(active_emergencies),
            'agency_emergencies': agency_emergencies,
            'agency_emergency_count': agency_emergency_count,
            'total_emergencies_this_month': total_emergencies_this_month,
            'total_emergencies_this_year': total_emergencies_this_year,
            'completed_emergencies_this_month': completed_emergencies_this_month,
            'completed_emergencies_this_year': completed_emergencies_this_year,
            'responders': agency.responders,
            'available_responders': available_responders,
            'engaged_responders': engaged_responders,
            'available_responders_count': len(available_responders),
            'engaged_responders_count': len(engaged_responders),
            'total_responders_count': len(agency.responders),
            'resources': agency.resources,
            'emojis': EVENT_TYPE_EMOJIS,
        }
        
        return data

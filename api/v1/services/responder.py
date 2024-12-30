from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.v1.models.emergency import Emergency, EVENT_TYPE_EMOJIS
from api.v1.models.responder import Responder
from api.v1.models.responder_emergency import ResponderEmergency


class ResponderService:
    
    @classmethod
    def get_responder_full_details(cls, db: Session, current_user):
        '''Fetch responder details and associated emergencies'''
        
        # Get the current date and calculate the start and end of the current year
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)

        # Calculate the start and end of the year
        start_of_year = datetime(now.year, 1, 1)
        end_of_year = datetime(now.year, 12, 31)
        
        responder = Responder.fetch_one_by_field(db, user_id=current_user.id)
        
        # Get responder emergencies with associated responders
        query = (
            db.query(ResponderEmergency)
            .join(Emergency, Emergency.id == ResponderEmergency.emergency_id)
            # .join(Responder, Responder.id == ResponderEmergency.responder_id)
            .filter(ResponderEmergency.responder_id == responder.id)
            .order_by(ResponderEmergency.created_at.desc())
        )
        responder_emergencies = query.all()
        responder_emergency_count = query.count()
        
        # Get all emergencies
        all_emergencies = Emergency.all(db)
        all_pending_emergencies = Emergency.fetch_by_field(db, order='asc', status='Pending')
        assigned_emergencies = query.filter(Emergency.status == 'In Progress').all()
        
        # Get total responder emergencies completed
        completed_emergencies_all_time = (
            query
            .filter(Emergency.status == 'completed')
            .count()
        )
        
        # Get total responder emergencies completed this month
        completed_emergencies_this_month = (
            query
            .filter(Emergency.status == 'completed')
            .filter(Emergency.created_at.between(start_of_month, end_of_month))
            .count()
        )
        
        # Get total responder emergencies completed in the past year
        completed_emergencies_this_year = (
            query
            .filter(Emergency.status == 'completed')
            .filter(Emergency.created_at.between(start_of_year, end_of_year))
            .count()
        )
        
        # Get total responder emergencies completed this month
        total_emergencies_this_month = (
            query
            .filter(Emergency.created_at.between(start_of_month, end_of_month))
            .count()
        )
        
        # Get total responder emergencies completed in the past year
        total_emergencies_this_year = (
            query
            .filter(Emergency.created_at.between(start_of_year, end_of_year))
            .count()
        )
        
        data = {
            'user': current_user,
            'responder': responder,
            'responder_emergencies': responder_emergencies,
            'emergencies': all_emergencies,
            'pending_emergencies': all_pending_emergencies,
            'assigned_emergencies': assigned_emergencies,
            'assigned_emergencies_count': len(assigned_emergencies),
            'total_emergencies_this_month': total_emergencies_this_month,
            'total_emergencies_this_year': total_emergencies_this_year,
            'completed_emergencies_this_month': completed_emergencies_this_month,
            'completed_emergencies_this_year': completed_emergencies_this_year,
            'total_assigned_emergencies_count': responder_emergency_count,
            'completed_emergencies_all_time': completed_emergencies_all_time,
            'completed_emergencies_percentage': ((completed_emergencies_all_time / responder_emergency_count) * 100) if responder_emergency_count > 0 else 0,
            'emojis': EVENT_TYPE_EMOJIS,
        }
        
        return data

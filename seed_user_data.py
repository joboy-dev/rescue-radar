from faker import Faker

from api.v1.models import *
from api.v1.models.user import UserRole
from api.v1.services.auth import AuthService


fake = Faker()

PASSWORD = 'fakeuser'

# Create uusers
for _ in range(15):
    user = User.create(
        email=fake.email(domain='gmail.com'),
        password=AuthService.hash_password(PASSWORD),
        role=UserRole.PUBLIC.value
    )
    Profile.create(
        user_id=user.id,
        username=fake.user_name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        phone_number=fake.phone_number()
    )
    print(user)


for _ in range(5):
    agency_user = User.create(
        email=fake.email(domain='gmail.com'),
        password=AuthService.hash_password(PASSWORD),
        role=UserRole.AGENCY_ADMIN.value
    )
    
    Profile.create(
        user_id=agency_user.id,
        username=fake.user_name(),
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        phone_number=fake.phone_number()
    )
    
    agency_name = fake.company()
    agency = Agency.create(
        creator_id=agency_user.id,
        name=agency_name,
        contact_email=f'{agency_name.lower().replace(' ', '')}@agency.com',
        contact_number=fake.phone_number()
    )
    
    for _ in range(15):
        responder_user = User.create(
            email=fake.email(domain='gmail.com'),
            password=AuthService.hash_password(PASSWORD),
            role=UserRole.RESPONDER.value
        )
        Profile.create(
            user_id=responder_user.id,
            username=fake.user_name(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone_number=fake.phone_number()
        )
        Responder.create(
            user_id=responder_user.id,
            agency_id=agency.id,
            contact_number=fake.phone_number()
        )
        
        print(responder_user)
    
    print(agency_user)
    print(agency)


for user in User.all(per_page=5000):
    print(f'Email: {user.email}')
    print(f'Password: {PASSWORD}')
    print('\n\n')

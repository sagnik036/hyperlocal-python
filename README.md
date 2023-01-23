# hyperlocal-python
A Proprietor to person delivery app
# features that will be implemented in m1
- authentication
  - login
    - User Login api, (user can login to the platform using this)
    - Using MobileNumber(as a username) and password
    - otp based login is also allowed
  - registration
    - User can signup to the platform
    - User can only signup if mobile number gets verified using the otp
    - Email can also be verified but it will be after signup gets completed
- profile
    - User can also forget the password using otp 
    - Email can also be verified but it will be after signup gets completed

# features that will be implemented in m2
- Shop Add and Vehicle add api
  - Delivery Person
    - Delivery person can add their vehicle
    - Fields - 
        1. Vehicle name
        2. Vehicle Number (no need if other sected)
        3. Vehcile Vehicle Type
            1. 2 wheeler
            2. 3 wheeler
            3. 4 wheeler
            4. other 
  - Proprietor
    - Admin Panel
      - If has shop
        - Fields
            - Shop Name
            - Shop Photo (max 3) (not at initial registration)
            - Shop Type (Charracter Field)
            - Shop Description
            - Shop GST NO.
            - Shop Location
            - note we have used GeoDjango for all the location related things in the models and OpenStreetView data for the map
      - If has no shop
            - can proceed towards the dashboard

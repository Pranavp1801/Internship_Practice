from fastapi import FastAPI,Query,HTTPException,status
from pydantic import BaseModel, Field
from typing import Optional
import math

app=FastAPI()

@app.post("/")
def home(name:str=Query(...)):
	return {"message":f"Wel-Come to MediCare Clinic Sir {name}"}

#List of doctors
doctors = [
    {
        "id": 1,
        "name": "Dr. Amit Sharma",
        "specialization": "Cardiologist",
        "fee": 800,
        "experience_year": 12,
        "is_available": True
    },
    {
        "id": 2,
        "name": "Dr. Priya Mehta",
        "specialization": "Dermatologist",
        "fee": 500,
        "experience_year": 8,
        "is_available": True
    },
    {
        "id": 3,
        "name": "Dr. Rahul Verma",
        "specialization": "Pediatrician",
        "fee": 600,
        "experience_year": 10,
        "is_available": False
    },
    {
        "id": 4,
        "name": "Dr. Sneha Kapoor",
        "specialization": "General",
        "fee": 400,
        "experience_year": 6,
        "is_available": True
    },
    {
        "id": 5,
        "name": "Dr. Vikram Singh",
        "specialization": "Cardiologist",
        "fee": 900,
        "experience_year": 15,
        "is_available": False
    },
    {
        "id": 6,
        "name": "Dr. Anjali Desai",
        "specialization": "Dermatologist",
        "fee": 550,
        "experience_year": 9,
        "is_available": True
    }
]	

#dynamic input class for doctors
class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: float = Field(..., gt=0)
    experience_year: int = Field(..., gt=0)
    is_available: bool = True

doctor_id_counter=7

@app.post("/doctors",status_code=status.HTTP_201_CREATED)
def add_doctor(doctor:NewDoctor):
    global doctor_id_counter
    for d in doctors:
        if d["name"].lower()==doctor.name.lower():
            raise HTTPException(status_code=400,detail="Doctor already exists")

    new_doctor={
        "id":doctor_id_counter,
        "name":doctor.name,
        "specialization":doctor.specialization,
        "fee":doctor.fee,
        "experience_year":doctor.experience_year,
        "is_available":doctor.is_available
    }

    doctors.append(new_doctor)
    doctor_id_counter+=1
    return new_doctor

#Display all the doctors
@app.get("/doctors")
def get_doctors():
    available = [d for d in doctors if d["is_available"]]
    
    return {
        "total": len(doctors),
        "available_count": len(available),
        "doctors": doctors
    }

#function to find the doctor
def find_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None

@app.get("/doctors/summary")
def get_summary():
	
    
    if not doctors:
        return {"message": "No doctors found"}
    
    max_exp = 0
    most_exp_name = ""

    for d in doctors:
        if d["experience_year"] > max_exp:
            max_exp = d["experience_year"]
            most_exp_name = d["name"]

    cheapest_fee = doctors[0]["fee"]
    for d in doctors:
        if d["fee"] < cheapest_fee:
            cheapest_fee = d["fee"]

    specialization_count = {}

    for d in doctors:
        spec = d["specialization"]

        if spec in specialization_count:
            specialization_count[spec] += 1
        else:
            specialization_count[spec] = 1

    return {
        "total": len(doctors),
        "available_count": len([d for d in doctors if d["is_available"]]),
        "most_experienced": most_exp_name,
        "cheapest_fee": cheapest_fee,
        "specialization_count": specialization_count
    }
    
def filter_doctors_logic(specialization=None, max_fee=None, min_experience=None, is_available=None):
    
    result = []

    for d in doctors:

        if specialization is not None and d["specialization"].lower() != specialization.lower():
            continue

        if max_fee is not None and d["fee"] > max_fee:
            continue

        if min_experience is not None and d["experience_year"] < min_experience:
            continue

        if is_available is not None and d["is_available"] != is_available:
            continue

        result.append(d)

    return result

@app.get("/doctors/filter")
def filter_doctors(
    specialization: Optional[str] = None,
    max_fee: Optional[int] = None,
    min_experience: Optional[int] = None,
    is_available: Optional[bool] = None
):
    
    filtered = filter_doctors_logic(
        specialization,
        max_fee,
        min_experience,
        is_available
    )

    return {
        "total": len(filtered),
        "doctors": filtered
    } 

@app.get("/doctors/search")
def search_doctors(keyword:str):
    result=[d for d in doctors if keyword.lower() in d["name"].lower() or keyword.lower() in d["specialization"].lower()]
    if not result:
        return {"message":"No doctors found","total_found":0}
    return {"total_found":len(result),"results":result}
 
@app.get("/doctors/sort")
def sort_doctors(sort_by:str=Query("fee"),order:str=Query("asc")):
    valid=["fee","name","experience_year"]
    if sort_by not in valid:
        raise HTTPException(status_code=400,detail="invalid sort_by")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail="invalid order")

    reverse=True if order=="desc" else False
    data=sorted(doctors,key=lambda d:d[sort_by],reverse=reverse)

    return {"sort_by":sort_by,"order":order,"count":len(data),"data":data}
 
@app.get("/doctors/page")
def paginate_doctors(page:int=1,limit:int=3):
    total=len(doctors)
    total_pages=math.ceil(total/limit)

    if page<1 or page>total_pages:
        raise HTTPException(status_code=400,detail="invalid page")

    start=(page-1)*limit
    end=start+limit
    data=doctors[start:end]

    return {"page":page,"limit":limit,"total":total,"total_pages":total_pages,"data":data}
 
@app.get("/doctors/browse")
def browse_doctors(keyword:str|None=None,sort_by:str="fee",order:str="asc",page:int=1,limit:int=4):
    data=doctors

    if keyword:
        data=[d for d in data if keyword.lower() in d["name"].lower() or keyword.lower() in d["specialization"].lower()]

    reverse=True if order=="desc" else False
    data=sorted(data,key=lambda d:d.get(sort_by),reverse=reverse)

    start=(page-1)*limit
    end=start+limit

    return {"total":len(data),"page":page,"data":data[start:end]}

 
#get function for finding the doctor by id
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id:int):
	
	doctor=find_doctor(doctor_id)
	if not doctor:
		return{"message":"Doctor not found"}
	return{"Doctor":doctor}

@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id:int,fee:int|None=Query(None), is_available:bool|None=Query(None)):
	for d in doctors:
		if d["id"]==doctor_id:
			if fee is not None:
				d["fee"]=fee
			if is_available is not None:
				d["is_available"]=is_available
			return d
	
	raise HTTPException(status_code=404,detail="doctor not found")
			

@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id:int):
    for d in doctors:
        if d["id"]==doctor_id:
            for a in appointments:
                if a["doctor_name"].lower()==d["name"].lower() and a["status"]=="scheduled":
                    raise HTTPException(status_code=400,detail="Doctor has scheduled appointments")

            doctors.remove(d)
            return {"message":"Doctor deleted"}

    raise HTTPException(status_code=404,detail="doctor not found")

appointments=[]
appt_counter=1

#appointment
@app.get("/appointments")
def get_appointments():	
	return{"total":len(appointments),"appointments":appointments}

#Support class
class AppointmentRequest(BaseModel):
    patient_name: str = Field(min_length=2)
    doctor_id: int = Field(gt=0)
    date: str = Field(min_length=8)
    reason: str = Field(min_length=5)
    appointment_type: str = "in-person"
    senior_citizen: bool=False
 
@app.post("/appointments")
def create_appointment(data: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(data.doctor_id)
    if not doctor:
        return {"message": "Doctor not found"}

    if not doctor["is_available"]:
        return {"message": "Doctor not available"}

    original_fee, final_fee = calculate_fee(
        doctor["fee"],
        data.appointment_type,
        data.senior_citizen
    )

    appointment = {
        "appointment_id": appt_counter,
        "patient_name": data.patient_name,
        "doctor_id":doctor["id"],
        "doctor_name": doctor["name"],
        "date": data.date,
        "appointment_type": data.appointment_type,
        "original_fee": original_fee,
        "final_fee": final_fee,
        "status": "scheduled"
    }

    appointments.append(appointment)
    doctor["is_available"]=False
    appt_counter += 1

    return appointment

@app.get("/appointments/search")
def search_appointments(patient_name:str):
    result=[a for a in appointments if patient_name.lower() in a["patient_name"].lower()]
    return {"count":len(result),"appointments":result}

@app.get("/appointments/sort")
def sort_appointments(sort_by:str=Query("final_fee"),order:str=Query("asc")):
    valid=["final_fee","date"]
    if sort_by not in valid:
        raise HTTPException(status_code=400,detail="invalid sort_by")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail="invalid order")

    reverse=True if order=="desc" else False
    data=sorted(appointments,key=lambda a:a[sort_by],reverse=reverse)

    return {"sort_by":sort_by,"order":order,"count":len(data),"data":data}

@app.get("/appointments/page")
def paginate_appointments(page:int=1,limit:int=3):
    total=len(appointments)
    total_pages=math.ceil(total/limit)

    if page<1 or page>total_pages:
        raise HTTPException(status_code=400,detail="invalid page")

    start=(page-1)*limit
    end=start+limit
    data=appointments[start:end]

    return {"page":page,"limit":limit,"total":total,"total_pages":total_pages,"data":data}


@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id:int):
    for a in appointments:
        if a["appointment_id"]==appointment_id:
            a["status"]="confirmed"
            return a

    raise HTTPException(status_code=404,detail="appointment not found")

@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id:int):
    for a in appointments:
        if a["appointment_id"]==appointment_id:
            a["status"]="cancelled"

            for d in doctors:
                if d["id"]==a["doctor_id"]:
                    d["is_available"]=True
                    break

            return a

    raise HTTPException(status_code=404,detail="appointment not found")

@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id:int):
    for a in appointments:
        if a["appointment_id"]==appointment_id:
            a["status"]="completed"
            return a

    raise HTTPException(status_code=404,detail="appointment not found")

@app.get("/appointments/active")
def get_active_appointments():
    active=[a for a in appointments if a["status"] in ["scheduled","confirmed"]]
    return {"count":len(active),"appointments":active}

@app.get("/appointments/by-doctor/{doctor_id}")
def get_appointments_by_doctor(doctor_id:int):
    result=[a for a in appointments if a["doctor_id"]==doctor_id]
    return {"count":len(result),"appointments":result}

#
def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool):
    
    if appointment_type.lower() == "video":
        fee = base_fee * 0.8
    elif appointment_type.lower() == "emergency":
        fee = base_fee * 1.5
    else:
        fee = base_fee

    original_fee = int(fee)

    if senior_citizen:
        fee = fee * 0.85
    return original_fee, int(fee)

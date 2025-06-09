from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...models import User, Employee, Payroll, Training
from ...services.nhost import nhost_client
from ...core.auth.roles import hr_role

router = APIRouter(prefix="/hr", tags=["HR"])

@router.get("/employees")
async def get_all_employees(
    current_user: User = Depends(hr_role())
):
    """Obtiene la lista de todos los empleados"""
    try:
        employees = await nhost_client.graphql.query(
            """
            query GetAllEmployees {
                employees {
                    id
                    user {
                        id
                        email
                        role
                    }
                    personal_info {
                        first_name
                        last_name
                        phone
                        address
                    }
                    employment_info {
                        position
                        department
                        hire_date
                        status
                    }
                    documents {
                        type
                        url
                        expiry_date
                    }
                }
            }
            """
        )
        return employees.get("data", {}).get("employees", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/employees")
async def create_employee(
    employee_data: dict,
    current_user: User = Depends(hr_role())
):
    """Crea un nuevo empleado"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateEmployee($employee_data: jsonb!) {
                insert_employees_one(object: $employee_data) {
                    id
                    user {
                        email
                        role
                    }
                    personal_info
                    employment_info
                }
            }
            """,
            {"employee_data": employee_data}
        )
        return result.get("data", {}).get("insert_employees_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payroll")
async def get_payroll(
    month: int,
    year: int,
    current_user: User = Depends(hr_role())
):
    """Obtiene la nómina del mes especificado"""
    try:
        payroll = await nhost_client.graphql.query(
            """
            query GetPayroll($month: Int!, $year: Int!) {
                payroll(
                    where: {
                        month: {_eq: $month},
                        year: {_eq: $year}
                    }
                ) {
                    id
                    employee {
                        id
                        user {
                            email
                        }
                    }
                    base_salary
                    bonuses
                    deductions
                    net_salary
                    status
                }
            }
            """,
            {"month": month, "year": year}
        )
        return payroll.get("data", {}).get("payroll", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payroll/process")
async def process_payroll(
    month: int,
    year: int,
    current_user: User = Depends(hr_role())
):
    """Procesa la nómina del mes especificado"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation ProcessPayroll($month: Int!, $year: Int!) {
                process_payroll(month: $month, year: $year) {
                    success
                    message
                    processed_count
                }
            }
            """,
            {"month": month, "year": year}
        )
        return result.get("data", {}).get("process_payroll", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training")
async def get_training_programs(
    current_user: User = Depends(hr_role())
):
    """Obtiene los programas de capacitación"""
    try:
        training = await nhost_client.graphql.query(
            """
            query GetTrainingPrograms {
                training_programs {
                    id
                    name
                    description
                    start_date
                    end_date
                    participants {
                        employee {
                            id
                            user {
                                email
                            }
                        }
                        status
                        completion_date
                    }
                }
            }
            """
        )
        return training.get("data", {}).get("training_programs", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training")
async def create_training_program(
    program_data: dict,
    current_user: User = Depends(hr_role())
):
    """Crea un nuevo programa de capacitación"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateTrainingProgram($program_data: jsonb!) {
                insert_training_programs_one(object: $program_data) {
                    id
                    name
                    description
                    start_date
                    end_date
                }
            }
            """,
            {"program_data": program_data}
        )
        return result.get("data", {}).get("insert_training_programs_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluations")
async def get_employee_evaluations(
    employee_id: str,
    current_user: User = Depends(hr_role())
):
    """Obtiene las evaluaciones de un empleado"""
    try:
        evaluations = await nhost_client.graphql.query(
            """
            query GetEmployeeEvaluations($employee_id: uuid!) {
                evaluations(
                    where: {employee_id: {_eq: $employee_id}}
                ) {
                    id
                    type
                    date
                    evaluator {
                        id
                        email
                    }
                    scores
                    comments
                    status
                }
            }
            """,
            {"employee_id": employee_id}
        )
        return evaluations.get("data", {}).get("evaluations", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluations")
async def create_evaluation(
    evaluation_data: dict,
    current_user: User = Depends(hr_role())
):
    """Crea una nueva evaluación de empleado"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation CreateEvaluation($evaluation_data: jsonb!) {
                insert_evaluations_one(object: $evaluation_data) {
                    id
                    type
                    date
                    employee_id
                    evaluator_id
                    scores
                    comments
                }
            }
            """,
            {"evaluation_data": evaluation_data}
        )
        return result.get("data", {}).get("insert_evaluations_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def get_employee_documents(
    employee_id: str,
    current_user: User = Depends(hr_role())
):
    """Obtiene los documentos de un empleado"""
    try:
        documents = await nhost_client.graphql.query(
            """
            query GetEmployeeDocuments($employee_id: uuid!) {
                employee_documents(
                    where: {employee_id: {_eq: $employee_id}}
                ) {
                    id
                    type
                    name
                    url
                    upload_date
                    expiry_date
                    status
                }
            }
            """,
            {"employee_id": employee_id}
        )
        return documents.get("data", {}).get("employee_documents", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents")
async def upload_employee_document(
    document_data: dict,
    current_user: User = Depends(hr_role())
):
    """Sube un nuevo documento de empleado"""
    try:
        result = await nhost_client.graphql.mutation(
            """
            mutation UploadEmployeeDocument($document_data: jsonb!) {
                insert_employee_documents_one(object: $document_data) {
                    id
                    type
                    name
                    url
                    upload_date
                    expiry_date
                }
            }
            """,
            {"document_data": document_data}
        )
        return result.get("data", {}).get("insert_employee_documents_one", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
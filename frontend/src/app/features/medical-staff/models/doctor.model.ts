// Debe coincidir con el JSON que devuelve
// backend/app/modules/medical_staff/api/routes.py.

export interface Doctor {
  doctorId: number;
  fullName: string;
  specialty: string;
}

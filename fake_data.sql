use clinic_system;
SET FOREIGN_KEY_CHECKS = 0;
select * from accounts_user;
-- Create a doctor profile
INSERT INTO doctors_doctorprofile (id, user_id, specialization, session_duration, buffer_time)
VALUES
  (1, 1, 'Family Medicine', 30, 10);

-- Create doctor schedules
INSERT INTO doctors_doctorschedule (id, doctor_id, day_of_week, start_time, end_time)
VALUES
  (1, 1, 'MON', '09:00:00', '13:00:00'),
  (2, 1, 'WED', '13:00:00', '17:00:00'),
  (3, 1, 'FRI', '09:00:00', '12:00:00');

-- Create a doctor schedule exception
INSERT INTO doctors_doctorscheduleexception (id, doctor_id, date, is_day_off, start_time, end_time)
VALUES
  (1, 1, '2026-05-01', 1, NULL, NULL);

-- Create appointments
INSERT INTO appointments_appointment (id, patient_id, doctor_id, appointment_date, start_time, end_time, status, check_in_time, created_at)
VALUES
  (1, 1, 3, '2026-05-02', '10:00:00', '10:30:00', 'confirmed', '2026-05-02 09:55:00', '2026-04-25 09:00:00'),
  (2, 4, 3, '2026-05-03', '14:00:00', '14:30:00', 'requested', NULL, '2026-04-25 09:10:00');

-- Create appointment reschedule history
INSERT INTO appointments_appointmentreschedule (id, appointment_id, old_date, old_time, new_date, new_time, changed_by_id, reason, created_at)
VALUES
  (1, 1, '2026-05-01', '10:00:00', '2026-05-02', '10:00:00', 2, 'Patient requested a later date.', '2026-04-25 09:20:00');

-- Create consultation data
INSERT INTO consultations_consultation (id, appointment_id, diagnosis, notes, created_at)
VALUES
  (1, 1, 'Upper respiratory infection', 'Prescribed rest and fluids.', '2026-05-02 10:35:00');

-- Create prescription records
INSERT INTO consultations_prescription (id, consultation_id, drug_name, dosage, duration)
VALUES
  (1, 1, 'Amoxicillin', '500mg twice daily', '7 days'),
  (2, 1, 'Paracetamol', '500mg every 6 hours as needed', '5 days');

-- Create medical test records
INSERT INTO consultations_medicaltest (id, consultation_id, test_name)
VALUES
  (1, 1, 'Complete Blood Count'),
  (2, 1, 'Chest X-ray');

-- Create notifications
INSERT INTO notifications_notification (id, user_id, title, message, notification_type, is_read, created_at)
VALUES
  (1, 1, 'Appointment confirmed', 'Your appointment on 2026-05-02 at 10:00 AM is confirmed.', 'confirmed', 0, '2026-04-25 09:05:00'),
  (2, 3, 'New appointment request', 'A new patient has requested an appointment on 2026-05-03.', 'confirmed', 0, '2026-04-25 09:12:00');

SET FOREIGN_KEY_CHECKS = 1;

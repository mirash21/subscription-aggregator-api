-- Insert test data for demonstration purposes
INSERT INTO subscriptions (service_name, price, user_id, start_date, end_date) VALUES
('Yandex Plus', 400, '60601fee-2bf1-4721-ae6f-7636e79a0cba', '2025-07-01', '2026-07-01'),
('Netflix Standard', 600, '60601fee-2bf1-4721-ae6f-7636e79a0cba', '2025-01-01', '2025-12-31'),
('Spotify Premium', 200, '60601fee-2bf1-4721-ae6f-7636e79a0cba', '2025-03-01', NULL),
('Apple Music', 150, '123e4567-e89b-12d3-a456-426614174000', '2025-05-01', '2026-05-01'),
('YouTube Premium', 300, '123e4567-e89b-12d3-a456-426614174000', '2025-02-01', NULL)
ON CONFLICT DO NOTHING;
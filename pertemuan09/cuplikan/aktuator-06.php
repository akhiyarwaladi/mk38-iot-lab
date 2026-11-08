$command->update(['status' => 'applied', 'acknowledged_at' => now()]);
$row->update(['reported_value' => $value, 'reported_at' => now(),
    'report_sequence' => $data['sequence']]);

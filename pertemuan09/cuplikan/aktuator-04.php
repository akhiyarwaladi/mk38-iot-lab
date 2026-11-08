$value = $request->input('value');
$max = $actuator->kind === 'led' ? 1 : 180;

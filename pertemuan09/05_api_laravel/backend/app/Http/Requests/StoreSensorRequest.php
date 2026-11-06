<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreSensorRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'device_id' => ['required', 'string', 'regex:/^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$/'],
            'suhu' => ['required', 'numeric', 'between:-40,80'],
            'kelembapan' => ['required', 'numeric', 'between:0,100'],
        ];
    }
}


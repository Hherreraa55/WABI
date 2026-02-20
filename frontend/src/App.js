import React, { useState, useEffect } from "react";
import "./App.css";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Smartphone, Building2, MapPin, User, CheckCircle, AlertCircle } from "lucide-react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}api`;

// Guatemala departments
const GUATEMALA_DEPARTMENTS = [
  "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula", "El Progreso",
  "Escuintla", "Guatemala", "Huehuetenango", "Izabal", "Jalapa", "Jutiapa",
  "Petén", "Quetzaltenango", "Quiché", "Retalhuleu", "Sacatepéquez",
  "San Marcos", "Santa Rosa", "Sololá", "Suchitepéquez", "Totonicapán", "Zacapa"
];

function App() {
  const [formData, setFormData] = useState({
    nombre: "",
    celular: "",
    nombre_negocio: "",
    departamento: "",
    municipio: "",
    numero_celular_negocio: ""
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const validateField = (name, value) => {
    const newErrors = { ...errors };

    switch (name) {
      case 'nombre':
        if (!value.trim()) {
          newErrors.nombre = "El nombre es obligatorio";
        } else if (value.length > 100) {
          newErrors.nombre = "El nombre no puede exceder 100 caracteres";
        } else {
          delete newErrors.nombre;
        }
        break;


      case 'celular':
      case 'numero_celular_negocio':
        const phone = value.replace(/[^\d]/g, '');
        if (!value.trim()) {
          newErrors[name] = "El número de celular es obligatorio";
        } else if (!/^502\d{8}$/.test(phone)) {
          newErrors[name] = "Formato: 502XXXXXXXX (ejemplo: 50255556666)";
        } else {
          delete newErrors[name];
        }
        break;

      case 'nombre_negocio':
        if (!value.trim()) {
          newErrors.nombre_negocio = "El nombre del negocio es obligatorio";
        } else if (value.length > 100) {
          newErrors.nombre_negocio = "Máximo 100 caracteres";
        } else {
          delete newErrors.nombre_negocio;
        }
        break;

      case 'departamento':
        if (!value) {
          newErrors.departamento = "Selecciona un departamento";
        } else {
          delete newErrors.departamento;
        }
        break;

      case 'municipio':
        if (!value.trim()) {
          newErrors.municipio = "El municipio es obligatorio";
        } else if (value.length > 100) {
          newErrors.municipio = "Máximo 100 caracteres";
        } else {
          delete newErrors.municipio;
        }
        break;

      default:
        break;
    }

    setErrors(newErrors);
  };

  const handleInputChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    validateField(name, value);
    setSubmitError("");
  };

  const validateForm = () => {
    const requiredFields = ['nombre', 'celular', 'nombre_negocio', 'departamento', 'municipio', 'numero_celular_negocio'];
    const newErrors = {};

    requiredFields.forEach(field => {
      if (!formData[field] || !formData[field].toString().trim()) {
        newErrors[field] = "Este campo es obligatorio";
      }
    });

    // Validate phone numbers
    ['celular', 'numero_celular_negocio'].forEach(field => {
      if (formData[field]) {
        const phone = formData[field].replace(/[^\d]/g, '');
        if (!/^502\d{8}$/.test(phone)) {
          newErrors[field] = "Formato: 502XXXXXXXX";
        }
      }
    });


    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setSubmitError("");

    try {
      const response = await axios.post(`${API}/store/`, {
        ...formData,
        celular: formData.celular.replace(/[^\d]/g, ''),
        numero_celular_negocio: formData.numero_celular_negocio.replace(/[^\d]/g, '')
      });

      if (response.data.success) {
        setSubmitted(true);
      }
    } catch (error) {
      if (error.response?.data?.detail) {
        setSubmitError(error.response.data.detail);
      } else {
        setSubmitError("Error al registrar. Por favor intenta de nuevo.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center">
          <CardContent className="pt-6">
            <div className="flex justify-center mb-4">
              <CheckCircle className="h-16 w-16 text-wabi-green" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              ¡Bienvenido a WABI!
            </h2>
            <p className="text-lg text-gray-600 mb-6">
              Tu negocio ya está en movimiento 🚀
            </p>
            <Button 
              onClick={() => window.location.reload()} 
              className="w-full bg-wabi-green hover:bg-green-600"
            >
              Registrar otro negocio
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-wabi-green mb-2">WABI</h1>
            <p className="text-gray-600 text-lg">Tu negocio en movimiento. Fácil y rápido.</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="shadow-lg border-0">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-2xl font-bold text-gray-900 mb-2">
              Únete a WABI
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              Registra tu negocio y empieza a crecer hoy mismo
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {submitError && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-600">
                    {submitError}
                  </AlertDescription>
                </Alert>
              )}

              {/* Personal Information Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <User className="h-5 w-5 text-wabi-green" />
                  Información Personal
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nombre" className="text-sm font-medium text-gray-700">
                      Nombre Completo *
                    </Label>
                    <Input
                      id="nombre"
                      type="text"
                      value={formData.nombre}
                      onChange={(e) => handleInputChange('nombre', e.target.value)}
                      className={`mt-1 ${errors.nombre ? 'border-red-300 focus:border-red-500' : ''}`}
                      placeholder="Tu nombre completo"
                    />
                    {errors.nombre && <p className="text-sm text-red-600 mt-1">{errors.nombre}</p>}
                  </div>

                </div>

                <div>
                  <Label htmlFor="celular" className="text-sm font-medium text-gray-700">
                    Celular Personal *
                  </Label>
                  <div className="relative mt-1">
                    <Smartphone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="celular"
                      type="tel"
                      value={formData.celular}
                      onChange={(e) => handleInpsasutChan('celular', e.target.value)}
                      className={`pl-10 ${errors.celular ? 'border-red-300 focus:border-red-500' : ''}`}
                      placeholder="502555566"
                    />
                  </div>
                  {errors.celular && <p className="text-sm text-red-600 mt-1">{errors.celular}</p>}
                </div>
              </div>

              {/* Business Information Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Building2 className="h-5 w-5 text-wabi-green" />
                  Información del Negocio
                </h3>

                <div>
                  <Label htmlFor="nombre_negocio" className="text-sm font-medium text-gray-700">
                    Nombre del Negocios *
                  </Label>
                  <Input
                    id="nombre_negocio"
                    type="text"
                    value={formData.nombre_negocio}
                    onChange={(e) => handleInputChange('nombre_negocio', e.target.value)}
                    className={`mt-1 ${errors.nombre_negocio ? 'border-red-300 focus:border-red-500' : ''}`}
                    placeholder="Mi Tienda"
                  />
                  {errors.nombre_negocio && <p className="text-sm text-red-600 mt-1">{errors.nombre_negocio}</p>}
                </div>

                <div>
                  <Label htmlFor="numero_celular_negocio" className="text-sm font-medium text-gray-700">
                    Celular del Negocio *
                  </Label>
                  <div className="relative mt-1">
                    <Smartphone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="numero_celular_negocio"
                      type="tel"
                      value={formData.numero_celular_negocio}
                      onChange={(e) => handleInputChange('numero_celular_negocio', e.target.value)}
                      className={`pl-10 ${errors.numero_celular_negocio ? 'border-red-300 focus:border-red-500' : ''}`}
                      placeholder="50244447777"
                    />
                  </div>
                  {errors.numero_celular_negocio && <p className="text-sm text-red-600 mt-1">{errors.numero_celular_negocio}</p>}
                </div>
              </div>

              {/* Location Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-wabi-green" />
                  Ubicación
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="departamento" className="text-sm font-medium text-gray-700">
                      Departamento *
                    </Label>
                    <Select value={formData.departamento} onValueChange={(value) => handleInputChange('departamento', value)}>
                      <SelectTrigger className={`mt-1 ${errors.departamento ? 'border-red-300 focus:border-red-500' : ''}`}>
                        <SelectValue placeholder="Selecciona departamento" />
                      </SelectTrigger>
                      <SelectContent>
                        {GUATEMALA_DEPARTMENTS.map((dept) => (
                          <SelectItem key={dept} value={dept}>
                            {dept}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.departamento && <p className="text-sm text-red-600 mt-1">{errors.departamento}</p>}
                  </div>

                  <div>
                    <Label htmlFor="municipio" className="text-sm font-medium text-gray-700">
                      Municipio *
                    </Label>
                    <Input
                      id="municipio"
                      type="text"
                      value={formData.municipio}
                      onChange={(e) => handleInputChange('municipio', e.target.value)}
                      className={`mt-1 ${errors.municipio ? 'border-red-300 focus:border-red-500' : ''}`}
                      placeholder="Tu municipio"
                    />
                    {errors.municipio && <p className="text-sm text-red-600 mt-1">{errors.municipio}</p>}
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-wabi-green hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 text-lg"
              >
                {isLoading ? "Registrando..." : "Registrar mi negocio en WABI"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500 text-sm">
          <p>© 2024 WABI. Todos los derechos reservados.</p>
        </div>
      </div>
    </div>
  );
}

export default App;
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    // Navegación simulada - Conecta con tu backend Python para autenticación real
    console.log("Iniciar sesión con Google - Conectar con backend Python");
    
    // Por ahora, navega directamente al chat para que puedas explorar la interfaz
    navigate("/chat");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-bbva-blue via-bbva-blue-light to-bbva-green p-4">
      <Card className="w-full max-w-md shadow-bbva">
        <CardHeader className="space-y-4 text-center">
          <CardTitle className="text-3xl font-bold text-primary">
            BBVA Sostenibilidad
          </CardTitle>
          <CardDescription className="text-base">
            Tu asistente virtual
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <Button
              onClick={handleGoogleLogin}
              variant="outline"
              className="w-full h-12 text-base font-medium border-2 hover:bg-muted transition-all"
            >
              <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Iniciar sesión con Google
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-border"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-card px-4 text-muted-foreground">
                  Acceso seguro y rápido
                </span>
              </div>
            </div>
          </div>

          <div className="text-center text-sm text-muted-foreground">
            <p>
              Al iniciar sesión, aceptas nuestros{" "}
              <a href="#" className="text-primary hover:underline font-medium">
                términos de servicio
              </a>{" "}
              y{" "}
              <a href="#" className="text-primary hover:underline font-medium">
                política de privacidad
              </a>
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="absolute bottom-4 text-center w-full">
        <p className="text-white/80 text-sm">
          Powered by BBVA | Compromiso con el medio ambiente
        </p>
      </div>
    </div>
  );
};

export default Login;

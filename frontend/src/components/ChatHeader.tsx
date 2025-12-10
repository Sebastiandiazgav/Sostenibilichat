import { Leaf, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

const ChatHeader = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Conectar con tu backend Python para logout
    console.log("Cerrar sesión - Conectar con backend Python");
    
    // Navega de vuelta al login
    navigate("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80 shadow-sm">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Leaf className="w-6 h-6 text-accent" />
          <div>
            <h1 className="text-lg font-bold text-primary">SostenibiliChat</h1>
            <p className="text-xs text-muted-foreground">Asistente Virtual de Sostenibilidad</p>
          </div>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          className="text-muted-foreground hover:text-foreground"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Salir
        </Button>
      </div>
    </header>
  );
};

export default ChatHeader;

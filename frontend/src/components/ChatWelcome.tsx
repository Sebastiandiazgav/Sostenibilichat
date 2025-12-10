import { Leaf, Lightbulb, TrendingUp, Shield } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const ChatWelcome = () => {
  const suggestions = [
    {
      icon: Leaf,
      title: "Captura de Operaciones Sostenibles",
      description: "cómo se identifican y capturan las operaciones sostenibles",
    },
    {
      icon: TrendingUp,
      title: "Parametrización y Escalado de Productos",
      description: "información sobre cómo se administra la parametría",
    },
    {
      icon: Lightbulb,
      title: "KPI Local de Sostenibilidad",
      description: "construcción del KPI de Sostenibilidad",
    },
    {
      icon: Shield,
      title: "Tablón Operativo",
      description: "cómo se genera, estructura y propósito del tablón",
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="max-w-3xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-foreground">
            Bienvenido a SostenibiliChat
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Bienvenido a SostenibiliChat, tu asistente virtual especializado en el proyecto corporativo de Sostenibilidad de BBVA.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {suggestions.map((suggestion, index) => (
            <Card
              key={index}
              className="cursor-pointer hover:shadow-md transition-all hover:border-primary/50"
            >
              <CardContent className="p-4 flex gap-3">
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                  <suggestion.icon className="w-5 h-5 text-accent" />
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-sm text-foreground">
                    {suggestion.title}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {suggestion.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Powered by <span className="font-semibold text-primary">BBVA</span> | Compromiso con el medio ambiente
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatWelcome;

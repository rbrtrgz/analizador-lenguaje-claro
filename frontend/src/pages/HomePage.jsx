import React, { useState } from 'react';
import { Textarea } from '../components/ui/textarea';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { MAX_CHARACTERS } from '../mock';
import { toast } from '../hooks/use-toast';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = () => {
  const [text, setText] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast({
        title: "Error",
        description: "Por favor, ingresa un texto para analizar",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/analyze`, {
        text: text
      });

      const sugerenciasWithState = response.data.sugerencias.map(s => ({
        ...s,
        accepted: null
      }));

      setAnalysis({ sugerencias: sugerenciasWithState });
      setSuggestions(sugerenciasWithState);
      
      toast({
        title: "Análisis completado",
        description: `Se encontraron ${sugerenciasWithState.length} sugerencias de mejora`
      });
    } catch (error) {
      console.error('Error al analizar el texto:', error);
      toast({
        title: "Error",
        description: error.response?.data?.detail || "No se pudo analizar el texto. Por favor, intenta de nuevo.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = (id) => {
    setSuggestions(suggestions.map(s => 
      s.id === id ? { ...s, accepted: true } : s
    ));
    toast({
      title: "Sugerencia aceptada",
      description: "La mejora ha sido aplicada"
    });
  };

  const handleReject = (id) => {
    setSuggestions(suggestions.map(s => 
      s.id === id ? { ...s, accepted: false } : s
    ));
    toast({
      title: "Sugerencia rechazada",
      description: "La mejora ha sido descartada"
    });
  };

  const handleReset = () => {
    setText('');
    setAnalysis(null);
    setSuggestions([]);
  };

  const getImprovedText = () => {
    let improvedText = text;
    suggestions.forEach(s => {
      if (s.accepted === true) {
        improvedText = improvedText.replace(s.original, s.sugerencia);
      }
    });
    return improvedText;
  };

  const charactersLeft = MAX_CHARACTERS - text.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-cyan-50">
      {/* Header */}
      <header className="border-b border-sky-100 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg shadow-cyan-200 p-2 border-2 border-cyan-200">
              <img src="/redactia-icon.png" alt="Redactia" className="w-full h-full object-contain" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Redactia: analizador de lenguaje claro</h1>
              <p className="text-sm text-gray-600">Una herramienta que ayuda a las administraciones públicas a redactar textos más claros y comprensibles, siguiendo las buenas prácticas de lenguaje claro.</p>
              <p className="text-xs text-gray-500 italic mt-1">Basado en la Guía Panhispánica de Lenguaje claro y accesible publicado por la R.A.E.</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <Card className="shadow-md border-sky-100">
              <CardHeader>
                <CardTitle className="text-xl">Texto a analizar</CardTitle>
                <CardDescription>
                  Pega aquí el texto administrativo que deseas mejorar
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative">
                  <Textarea
                    value={text}
                    onChange={(e) => {
                      if (e.target.value.length <= MAX_CHARACTERS) {
                        setText(e.target.value);
                      }
                    }}
                    placeholder="Ejemplo: Con relación a la presente comunicación, procedemos a informarle que..."
                    className="min-h-[300px] resize-none border-sky-200 focus:border-cyan-400 focus:ring-cyan-400"
                    maxLength={MAX_CHARACTERS}
                  />
                  <div className="absolute bottom-3 right-3">
                    <Badge 
                      variant={charactersLeft < 500 ? "destructive" : "secondary"}
                      className={charactersLeft < 500 ? "" : "bg-sky-100 text-sky-700 border-sky-200"}
                    >
                      {charactersLeft} caracteres restantes
                    </Badge>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Button 
                    onClick={handleAnalyze} 
                    disabled={loading || !text.trim()}
                    className="flex-1 bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-600 hover:to-sky-600 text-white shadow-md shadow-cyan-200 transition-all duration-200"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Analizando...
                      </>
                    ) : (
                      <>
                        <AlertCircle className="w-4 h-4 mr-2" />
                        Analizar texto
                      </>
                    )}
                  </Button>
                  {analysis && (
                    <Button 
                      onClick={handleReset} 
                      variant="outline"
                      className="border-sky-200 hover:bg-sky-50 hover:border-sky-300 transition-all duration-200"
                    >
                      Nuevo análisis
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            {analysis && suggestions.length > 0 ? (
              <Card className="shadow-md border-sky-100">
                <CardHeader>
                  <CardTitle className="text-xl">Sugerencias de mejora</CardTitle>
                  <CardDescription>
                    {suggestions.length} problema{suggestions.length !== 1 ? 's' : ''} detectado{suggestions.length !== 1 ? 's' : ''}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[500px] pr-4">
                    <div className="space-y-4">
                      {suggestions.map((suggestion) => (
                        <Card 
                          key={suggestion.id} 
                          className={`border-2 transition-all duration-300 ${
                            suggestion.accepted === true 
                              ? 'border-cyan-400 bg-cyan-50/50 shadow-sm shadow-cyan-200' 
                              : suggestion.accepted === false 
                              ? 'border-gray-300 bg-gray-50 opacity-60' 
                              : 'border-sky-100 hover:border-sky-200 hover:shadow-sm'
                          }`}
                        >
                          <CardContent className="pt-6 space-y-3">
                            <div className="space-y-2">
                              <div className="flex items-start gap-2">
                                <Badge className="bg-red-100 text-red-700 border-red-200 hover:bg-red-100">
                                  Original
                                </Badge>
                                <p className="text-sm text-gray-700 flex-1 line-through">
                                  {suggestion.original}
                                </p>
                              </div>
                              <div className="flex items-start gap-2">
                                <Badge className="bg-cyan-100 text-cyan-700 border-cyan-200 hover:bg-cyan-100">
                                  Sugerencia
                                </Badge>
                                <p className="text-sm text-gray-900 flex-1 font-medium">
                                  {suggestion.sugerencia}
                                </p>
                              </div>
                              <div className="flex items-start gap-2">
                                <Badge variant="outline" className="border-sky-200 text-sky-700">
                                  Problema
                                </Badge>
                                <p className="text-xs text-gray-600 flex-1 italic">
                                  {suggestion.problema}
                                </p>
                              </div>
                            </div>
                            {suggestion.accepted === null && (
                              <div className="flex gap-2 pt-2">
                                <Button
                                  onClick={() => handleAccept(suggestion.id)}
                                  size="sm"
                                  className="flex-1 bg-gradient-to-r from-cyan-500 to-sky-500 hover:from-cyan-600 hover:to-sky-600 text-white transition-all duration-200"
                                >
                                  <CheckCircle2 className="w-4 h-4 mr-1" />
                                  Aceptar
                                </Button>
                                <Button
                                  onClick={() => handleReject(suggestion.id)}
                                  size="sm"
                                  variant="outline"
                                  className="flex-1 border-sky-200 hover:bg-sky-50 transition-all duration-200"
                                >
                                  <XCircle className="w-4 h-4 mr-1" />
                                  Rechazar
                                </Button>
                              </div>
                            )}
                            {suggestion.accepted === true && (
                              <div className="flex items-center justify-center gap-2 pt-2 text-cyan-600">
                                <CheckCircle2 className="w-4 h-4" />
                                <span className="text-sm font-medium">Sugerencia aceptada</span>
                              </div>
                            )}
                            {suggestion.accepted === false && (
                              <div className="flex items-center justify-center gap-2 pt-2 text-gray-500">
                                <XCircle className="w-4 h-4" />
                                <span className="text-sm font-medium">Sugerencia rechazada</span>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            ) : (
              <Card className="shadow-md border-sky-100">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mb-4 p-4 border-2 border-cyan-200 shadow-md shadow-cyan-100">
                      <img src="/redactia-icon.png" alt="Redactia" className="w-full h-full object-contain" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Sin análisis todavía
                    </h3>
                    <p className="text-sm text-gray-600 max-w-sm">
                      Ingresa un texto administrativo y haz clic en "Analizar texto" para obtener sugerencias de mejora
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Improved Text Preview */}
            {analysis && suggestions.some(s => s.accepted === true) && (
              <Card className="shadow-md border-cyan-200 bg-gradient-to-br from-cyan-50 to-sky-50">
                <CardHeader>
                  <CardTitle className="text-xl text-cyan-900">Texto mejorado</CardTitle>
                  <CardDescription>
                    Vista previa con las sugerencias aceptadas aplicadas
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-white rounded-lg p-4 border border-cyan-200 shadow-sm">
                    <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                      {getImprovedText()}
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-sky-100 bg-white/80 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-gray-600">
          <p>Analizador basado en la Guía panhispánica de lenguaje claro (RAE)</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
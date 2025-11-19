// Mock data para desarrollo del frontend
export const mockAnalysis = {
  sugerencias: [
    {
      id: 1,
      original: "En relación a la presente comunicación",
      problema: "Expresión burocrática innecesaria.",
      sugerencia: "Sobre este mensaje",
      accepted: null
    },
    {
      id: 2,
      original: "procedemos a comunicarle",
      problema: "Locución redundante y poco directa.",
      sugerencia: "le informamos",
      accepted: null
    },
    {
      id: 3,
      original: "a los efectos oportunos",
      problema: "Expresión vacía sin contenido informativo.",
      sugerencia: "Eliminar (no aporta información)",
      accepted: null
    },
    {
      id: 4,
      original: "rogamos tenga a bien",
      problema: "Fórmula de cortesía excesiva y anticuada.",
      sugerencia: "le pedimos que",
      accepted: null
    }
  ]
};

export const MAX_CHARACTERS = 4000;
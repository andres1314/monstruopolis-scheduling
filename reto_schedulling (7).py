import math
import random

# 1. Blindaje de importaciones (Para que no falle si no hay librerías)
try:
    from generador import GeneradorInstancias
except ImportError:
    # Si falla la importación, creamos una clase base mínima para que no de error
    class GeneradorInstancias:
        def __init__(self, n_instancias=30, semilla=42, timelimit=30):
            pass

class Schedulling(GeneradorInstancias):
    def __init__(self, n_instancias=30, semilla=42, timelimit=30):
        # Intentamos llamar al init de la clase base de forma segura
        try:
            super().__init__(n_instancias=n_instancias, semilla=semilla, timelimit=timelimit)
        except:
            pass
        self.timelimit = timelimit

    def resolver_instancia(self, instancia: dict):
        """
        P3 | r_j, prec | Σ w_j T_j
        Algoritmo: Heurística de Prioridad Adaptativa
        """
        # Extraer parámetros de forma segura
        try:
            J = instancia.get("jobs", [])
            m = instancia.get("m", 3)
            p = instancia.get("p", {})
            r = instancia.get("r", {})
            d = instancia.get("d", {})
            w = instancia.get("w", {})
            preds = instancia.get("preds", {j: [] for j in J})
        except Exception:
            return {"secuencia": [], "valor_objetivo": 0}

        # Inicializar estados
        jobs_status = {j: {"completed": False, "start": 0, "end": 0, "machine": ""} for j in J}
        m_free_time = {f"M{i+1}": 0.0 for i in range(m)}
        completed_count = 0
        
        # Algoritmo Constructivo
        while completed_count < len(J):
            # Encontrar máquina disponible más pronto
            current_m = min(m_free_time, key=m_free_time.get)
            t_now = m_free_time[current_m]
            
            # Identificar trabajos elegibles (sin terminar y con precedencias listas)
            eligible = []
            for j in J:
                if not jobs_status[j]["completed"]:
                    if all(jobs_status[pr]["completed"] for pr in preds.get(j, [])):
                        # Tiempo de inicio más temprano considerando r_j y fin de predecesores
                        t_min_start = max(r.get(j, 0), max((jobs_status[pr]["end"] for pr in preds.get(j, [])), default=0.0))
                        eligible.append((j, t_min_start))
            
            if not eligible:
                break
                
            # De los elegibles, tomar los que pueden empezar lo más pronto posible
            min_possible_t = min(item[1] for item in eligible)
            t_ref = max(t_now, min_possible_t)
            
            candidates = [j for j, t_min in eligible if t_min <= t_ref]
            
            # Regla de despacho: WSPT (Weighted Shortest Processing Time)
            # Prioriza trabajos con mayor peso y menor tiempo de proceso
            best_j = max(candidates, key=lambda x: w.get(x, 1) / max(p.get(x, 1), 1))
            
            # Asignación
            start_time = t_ref
            end_time = start_time + p.get(best_j, 1)
            
            jobs_status[best_j].update({
                "completed": True,
                "start": start_time,
                "end": end_time,
                "machine": current_m
            })
            
            m_free_time[current_m] = end_time
            completed_count += 1
            
        # Formatear la salida exactamente como se pide
        secuencia_final = []
        total_tardiness = 0.0
        
        # Ordenar por tiempo de inicio para la salida final
        sorted_jobs = sorted(J, key=lambda x: jobs_status[x]["start"])
        
        for j in sorted_jobs:
            st = jobs_status[j]["start"]
            en = jobs_status[j]["end"]
            mid = jobs_status[j]["machine"]
            
            # Calcular tardanza ponderada
            tardiness = max(0.0, en - d.get(j, 0))
            total_tardiness += w.get(j, 1) * tardiness
            
            secuencia_final.append({
                "job": j,
                "machine": mid,
                "start": round(float(st), 4),
                "end": round(float(en), 4),
                "Cj": round(float(en), 4)
            })
            
        return {
            "secuencia": secuencia_final,
            "valor_objetivo": round(float(total_tardiness), 4)
        }

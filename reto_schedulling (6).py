import math

# Intentar importar la clase base, pero sin que sea un error fatal
try:
    from generador import GeneradorInstancias
except ImportError:
    class GeneradorInstancias:
        def __init__(self, **kwargs): pass

class Schedulling(GeneradorInstancias):
    def __init__(self, n_instancias=30, semilla=42, timelimit=30):
        try:
            super().__init__(n_instancias=n_instancias, semilla=semilla, timelimit=timelimit)
        except:
            pass

    def resolver_instancia(self, instancia):
        # 1. Extraer datos
        J = instancia["jobs"]
        m = instancia["m"]
        p, r, d, w = instancia["p"], instancia["r"], instancia["d"], instancia["w"]
        preds = instancia["preds"]

        # 2. Inicializar estado
        status = {j: {"done": False, "start": 0, "end": 0, "m": ""} for j in J}
        m_free = {f"M{i+1}": 0.0 for i in range(m)}
        done_count = 0

        # 3. Heurística simple y robusta
        while done_count < len(J):
            # Máquina disponible más pronto
            mid = min(m_free, key=m_free.get)
            t_now = m_free[mid]

            # Candidatos (sin terminar y con predecesores listos)
            ready = []
            for j in J:
                if not status[j]["done"]:
                    if all(status[pr]["done"] for pr in preds[j]):
                        # Tiempo mínimo de inicio para este trabajo
                        t_min = max(r[j], max((status[pr]["end"] for pr in preds[j]), default=0.0))
                        ready.append((j, t_min))

            if not ready: break

            # De los listos, elegir los que pueden empezar en t_now (o el más cercano)
            t_earliest = min(item[1] for item in ready)
            t_ref = max(t_now, t_earliest)
            
            candidates = [j for j, t_min in ready if t_min <= t_ref]
            
            # Regla de despacho: Prioridad WSPT (w_j / p_j) para minimizar tardanza
            best_j = max(candidates, key=lambda x: w[x]/p[x])

            # Asignar
            start_t = t_ref
            end_t = start_t + p[best_j]
            
            status[best_j].update({"done": True, "start": start_t, "end": end_t, "m": mid})
            m_free[mid] = end_t
            done_count += 1

        # 4. Formatear salida exacta
        sec = []
        obj = 0.0
        for j in sorted(J, key=lambda x: status[x]["start"]):
            s, e, mid = status[j]["start"], status[j]["end"], status[j]["m"]
            obj += w[j] * max(0.0, e - d[j])
            sec.append({"job": j, "machine": mid, "start": round(s, 2), "end": round(e, 2), "Cj": round(e, 2)})

        return {"secuencia": sec, "valor_objetivo": round(obj, 2)}

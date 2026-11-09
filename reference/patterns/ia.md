# IA: grupos, waypoints, patrullas y grupos atascados

```c
// grupo defendiendo un sitio
SCR_AIGroup g = XX_Util.SpawnGroup(grupoPrefab, pos, XX_Prefabs.WP_DEFEND, pos);

// patrulla en circulo con N paradas que se repite
void AddPatrolLoop(SCR_AIGroup g, vector center, float radius, int stops)
{
	array<AIWaypoint> wps = {};
	float start = Math.RandomFloat(0, Math.PI2);
	for (int i = 0; i < stops; i++)
	{
		float a = start + i * Math.PI2 / stops;
		vector p = XX_Util.OnNavmesh(center + Vector(Math.Cos(a) * radius, 0, Math.Sin(a) * radius));
		AIWaypoint wp = AIWaypoint.Cast(XX_Util.Spawn(XX_Prefabs.WP_PATROL, p));
		if (wp)
			wps.Insert(wp);
	}
	AIWaypointCycle cycle = AIWaypointCycle.Cast(XX_Util.Spawn(XX_Prefabs.WP_CYCLE, center));
	if (!cycle)
	{
		foreach (AIWaypoint w : wps)
			g.AddWaypoint(w);
		return;
	}
	cycle.SetWaypoints(wps);
	g.AddWaypoint(cycle);
}

// quitar los waypoints de un grupo (para darle otra orden)
static void ClearWaypoints(SCR_AIGroup g)
{
	array<AIWaypoint> wps = {};
	g.GetWaypoints(wps);
	foreach (AIWaypoint w : wps)
		g.RemoveWaypoint(w);
}
```

## Grupos atascados

Cada pocos segundos, guarda la posición de cada grupo que tenga una ruta (no Defend o Wait). Si en 120 s no se ha movido más de 4 m, quítale los waypoints y dale una patrulla nueva alrededor de donde está. Esto evita grupos parados por un punto sin camino o una puerta cerrada.

## Rendimiento

- **No tengas cientos de soldados a la vez.** Crea las guarniciones al acercarse los jugadores (radio 800-1500 m) y bórralas al irse, guardando cuántos quedaban.
- **Comprueba si quedan vivos con `g.GetAgentsCount()`.** Un grupo vacío se borra solo.

## Grupos de cada facción

`python tools/find.py Group <FACCION> .et`. Por ejemplo, `Group USSR`, `Group US`, `Group FIA`, o los de RHS (`Group_RHS_RF_MSV`) y FFAA.

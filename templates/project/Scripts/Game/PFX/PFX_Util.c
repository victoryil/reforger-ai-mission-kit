// {{TITLE}} - utilidades comunes (crear entidades, suelo, navmesh, jugadores).
// Patrones probados en misiones reales: ver docs/03-lecciones-enfusion.md del kit.

class {{P}}_Util
{
	//! Crea un prefab en una posicion y orientacion (grados). Avisa en el log si el prefab no carga.
	static IEntity Spawn(ResourceName prefab, vector pos, float yaw = 0)
	{
		if (prefab.IsEmpty())
			return null;
		Resource res = Resource.Load(prefab);
		if (!res || !res.IsValid())
		{
			Print("[{{P}}] No se puede cargar el prefab " + prefab, LogLevel.WARNING);
			return null;
		}
		EntitySpawnParams params = new EntitySpawnParams();
		params.TransformMode = ETransformMode.WORLD;
		Math3D.AnglesToMatrix(Vector(yaw, 0, 0), params.Transform);
		params.Transform[3] = pos;
		return GetGame().SpawnEntityPrefab(res, GetGame().GetWorld(), params);
	}

	//! La misma posicion a ras de suelo
	static vector Ground(vector pos)
	{
		BaseWorld world = GetGame().GetWorld();
		if (world)
			pos[1] = world.GetSurfaceY(pos[0], pos[2]);
		return pos;
	}

	//! Punto alcanzable de la navmesh de soldados cerca de p, a ras de suelo (sin tejados ni pisos altos).
	//! Usalo SIEMPRE para grupos y waypoints de IA: si no, "Failed move" y la IA se queda quieta.
	static vector OnNavmesh(vector p, float searchDist = 40)
	{
		p = Ground(p);
		AIWorld ai = GetGame().GetAIWorld();
		if (!ai)
			return p;
		NavmeshWorldComponent nav = ai.GetNavmeshWorldComponent("Soldiers");
		if (!nav)
			return p;
		if (!nav.IsTileLoaded(p))
			nav.LoadTileIn(p);
		vector outPos;
		BaseWorld world = GetGame().GetWorld();
		for (int k = 0; k < 6; k++)
		{
			vector q = p;
			if (k > 0)
				q = Ground(p + Vector(Math.RandomFloat(-searchDist, searchDist) * 0.5, 0, Math.RandomFloat(-searchDist, searchDist) * 0.5));
			if (!nav.GetReachablePoint(q, searchDist, outPos))
				continue;
			if (world && outPos[1] - world.GetSurfaceY(outPos[0], outPos[2]) > 1.5)
				continue;
			return outPos;
		}
		return p;
	}

	static vector RandomAround(vector center, float minR, float maxR)
	{
		float ang = Math.RandomFloat(0, Math.PI2);
		float r = Math.RandomFloat(minR, maxR);
		return Ground(center + Vector(Math.Cos(ang) * r, 0, Math.Sin(ang) * r));
	}

	static bool IsAlive(IEntity ent)
	{
		if (!ent)
			return false;
		ChimeraCharacter character = ChimeraCharacter.Cast(ent);
		if (character)
		{
			CharacterControllerComponent ctrl = character.GetCharacterController();
			if (ctrl)
				return !ctrl.IsDead();
		}
		DamageManagerComponent dmg = DamageManagerComponent.Cast(ent.FindComponent(DamageManagerComponent));
		if (dmg)
			return !dmg.IsDestroyed();
		return true;
	}

	static void AlivePlayers(notnull array<IEntity> outEntities)
	{
		array<int> ids = {};
		GetGame().GetPlayerManager().GetPlayers(ids);
		foreach (int id : ids)
		{
			IEntity ent = GetGame().GetPlayerManager().GetPlayerControlledEntity(id);
			if (IsAlive(ent))
				outEntities.Insert(ent);
		}
	}

	//! Algun jugador vivo a menos de r metros (en el plano) de pos
	static bool AnyPlayerNear(vector pos, float r)
	{
		array<IEntity> players = {};
		AlivePlayers(players);
		foreach (IEntity p : players)
		{
			if (vector.DistanceXZ(p.GetOrigin(), pos) < r)
				return true;
		}
		return false;
	}

	//! Grupo de IA en el suelo de la navmesh, con un waypoint opcional
	static SCR_AIGroup SpawnGroup(ResourceName groupPrefab, vector pos, ResourceName waypointPrefab = "", vector waypointPos = vector.Zero)
	{
		SCR_AIGroup g = SCR_AIGroup.Cast(Spawn(groupPrefab, OnNavmesh(pos)));
		if (!g)
			return null;
		if (!waypointPrefab.IsEmpty())
		{
			if (waypointPos == vector.Zero)
				waypointPos = pos;
			AIWaypoint wp = AIWaypoint.Cast(Spawn(waypointPrefab, OnNavmesh(waypointPos)));
			if (wp)
				g.AddWaypoint(wp);
		}
		return g;
	}

	//! Soldados vivos de un grupo (0 si ya no existe)
	static int AliveInGroup(SCR_AIGroup g)
	{
		if (!g)
			return 0;
		return g.GetAgentsCount();
	}

	//! Vuelca al log los sitios con nombre del mapa (ciudades, pueblos, bases, puertos...) con su posicion a ras
	//! de suelo. Se activa con -{{P}}DumpMap; tools/map_locations.py lo convierte en una tabla para elegir sitios.
	static void DumpMap()
	{
		SCR_MapEntity mapEnt = SCR_MapEntity.GetMapInstance();
		if (!mapEnt)
		{
			Print("[MAP] FIN (no hay SCR_MapEntity en el mundo)", LogLevel.NORMAL);
			return;
		}
		array<int> types = { EMapDescriptorType.MDT_NAME_CITY, EMapDescriptorType.MDT_NAME_TOWN, EMapDescriptorType.MDT_NAME_VILLAGE, EMapDescriptorType.MDT_NAME_SETTLEMENT, EMapDescriptorType.MDT_NAME_LOCAL, EMapDescriptorType.MDT_NAME_GENERIC, EMapDescriptorType.MDT_NAME_ISLAND, EMapDescriptorType.MDT_BASE, EMapDescriptorType.MDT_PORT, EMapDescriptorType.MDT_AIRPORT };
		array<string> names = { "ciudad", "pueblo", "aldea", "asentamiento", "lugar", "generico", "isla", "base", "puerto", "aeropuerto" };
		foreach (int i, int t : types)
		{
			array<MapItem> items = {};
			mapEnt.GetByType(items, t);
			foreach (MapItem item : items)
			{
				IEntity ent = item.Entity();
				if (!ent)
					continue;
				vector pos = Ground(ent.GetOrigin());
				// el nombre viene como clave de traduccion (#AR-MapLocation_...): se traduce si se puede
				string label = WidgetManager.Translate(item.GetDisplayName());
				if (label.IsEmpty())
					label = item.GetDisplayName();
				Print(string.Format("[MAP]	%1	%2	%3 %4 %5", names[i], label, Math.Round(pos[0]), Math.Round(pos[1] * 10) / 10, Math.Round(pos[2])), LogLevel.NORMAL);
			}
		}
		Print("[MAP] FIN", LogLevel.NORMAL);
	}

	//! Segundos de juego desde que empezo el mundo
	static float Now()
	{
		return GetGame().GetWorld().GetWorldTime() / 1000.0;
	}
}

class {{P}}_Prefabs
{
	// waypoints del juego base (comprobados)
	static const ResourceName WP_MOVE = "{750A8D1695BD6998}Prefabs/AI/Waypoints/AIWaypoint_Move.et";
	static const ResourceName WP_DEFEND = "{93291E72AC23930F}Prefabs/AI/Waypoints/AIWaypoint_Defend.et";
	static const ResourceName WP_PATROL = "{22A875E30470BD4F}Prefabs/AI/Waypoints/AIWaypoint_Patrol.et";
	static const ResourceName WP_SAD = "{B3E7B8DC2BAB8ACC}Prefabs/AI/Waypoints/AIWaypoint_SearchAndDestroy.et";
	static const ResourceName WP_CYCLE = "{35BD6541CBB8AC08}Prefabs/AI/Waypoints/AIWaypoint_Cycle.et";

	// grupos enemigos: cambialos por los de tu faccion (python tools/find.py Group <faccion> .et)
	static const ResourceName ENEMY_GROUP = "{{ENEMY_GROUP}}";
}

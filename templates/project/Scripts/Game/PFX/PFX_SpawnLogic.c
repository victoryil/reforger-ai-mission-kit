// {{TITLE}} - aparicion directa sin pantalla de seleccion: faccion del jugador, su unico equipo del
// gestor de equipos y el punto de aparicion "{{P}}_PlayerSpawn" (si no existe, cualquiera de la faccion).

[BaseContainerProps(category: "Respawn")]
class {{P}}_SpawnLogic : SCR_AutoSpawnLogic
{
	static const string PLAYER_FACTION = "{{PLAYER_FACTION_KEY}}";
	static const string SPAWN_ENTITY = "{{P}}_PlayerSpawn";

	override protected void DoSpawn_S(int playerId)
	{
		Faction faction = GetGame().GetFactionManager().GetFactionByKey(PLAYER_FACTION);
		if (!faction)
		{
			Print("[{{P}}] Aparicion: no existe la faccion " + PLAYER_FACTION, LogLevel.ERROR);
			return;
		}
		GetPlayerFactionComponent_S(playerId).RequestFaction(faction);
		SCR_BasePlayerLoadout loadout = GetGame().GetLoadoutManager().GetRandomFactionLoadout(faction);
		if (!loadout)
		{
			Print("[{{P}}] Aparicion: no hay equipo para la faccion en el gestor de equipos", LogLevel.ERROR);
			OnPlayerSpawnFailed_S(playerId);
			return;
		}
		GetPlayerLoadoutComponent_S(playerId).RequestLoadout(loadout);
		if (!GetPlayerFactionComponent_S(playerId).GetAffiliatedFaction() || !GetPlayerLoadoutComponent_S(playerId).GetLoadout())
		{
			OnPlayerSpawnFailed_S(playerId);
			return;
		}
		SCR_SpawnPoint point = SCR_SpawnPoint.Cast(GetGame().GetWorld().FindEntityByName(SPAWN_ENTITY));
		if (!point)
			point = SCR_SpawnPoint.GetRandomSpawnPointForFaction(faction.GetFactionKey());
		if (!point)
		{
			OnPlayerSpawnFailed_S(playerId);
			return;
		}
		SCR_SpawnPointSpawnData data = new SCR_SpawnPointSpawnData(loadout.GetLoadoutResource(), point.GetRplId());
		if (!GetPlayerRespawnComponent_S(playerId).CanSpawn(data))
		{
			OnPlayerSpawnFailed_S(playerId);
			return;
		}
		GetPlayerRespawnComponent_S(playerId).RequestSpawn(data);
	}
}

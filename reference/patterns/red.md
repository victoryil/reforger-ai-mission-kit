# Red: peticiones del jugador al servidor y respuestas solo a él

Todo jugador tiene un `SCR_PlayerControllerGroupComponent` en su PlayerController. Con `modded class` le añades tus RPC sin tocar prefabs. Probado en misiones con dos jugadores reales.

```c
enum XX_EReq { BUY, RECRUIT, STATUS }

modded class SCR_PlayerControllerGroupComponent
{
	//! Cliente: pide algo al servidor (en partida alojada se ejecuta directamente)
	void XX_Send(int kind, string arg, RplId source)
	{
		if (Replication.IsServer())
		{
			XX_Requests.Handle(XX_GetPlayerId(), kind, arg, source);
			return;
		}
		Rpc(XX_RpcAsk, kind, arg, source);
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void XX_RpcAsk(int kind, string arg, RplId source)
	{
		XX_Requests.Handle(XX_GetPlayerId(), kind, arg, source);   // el pid lo pone el servidor, no el cliente
	}

	//! Servidor: aviso solo para este jugador
	void XX_Tell(string title, string text)
	{
		PlayerController pc = PlayerController.Cast(GetOwner());
		if (pc && pc == GetGame().GetPlayerController())
		{
			XX_RpcDoTell(title, text);   // es el jugador local (partida alojada)
			return;
		}
		Rpc(XX_RpcDoTell, title, text);
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Owner)]
	protected void XX_RpcDoTell(string title, string text)
	{
		SCR_HintManagerComponent.ShowCustomHint(text, title, 8);
	}

	protected int XX_GetPlayerId()
	{
		PlayerController pc = PlayerController.Cast(GetOwner());
		if (pc)
			return pc.GetPlayerId();
		return -1;
	}

	static SCR_PlayerControllerGroupComponent XX_GetLocal()
	{
		PlayerController pc = GetGame().GetPlayerController();
		if (!pc)
			return null;
		return SCR_PlayerControllerGroupComponent.Cast(pc.FindComponent(SCR_PlayerControllerGroupComponent));
	}

	static SCR_PlayerControllerGroupComponent XX_GetFor(int playerId)
	{
		PlayerController pc = GetGame().GetPlayerManager().GetPlayerController(playerId);
		if (!pc)
			return null;
		return SCR_PlayerControllerGroupComponent.Cast(pc.FindComponent(SCR_PlayerControllerGroupComponent));
	}
}

class XX_Net
{
	static void Send(int kind, string arg, IEntity source)
	{
		SCR_PlayerControllerGroupComponent c = SCR_PlayerControllerGroupComponent.XX_GetLocal();
		if (!c)
			return;
		RplId id = RplId.Invalid();
		if (source)
		{
			RplComponent rpl = RplComponent.Cast(source.FindComponent(RplComponent));
			if (rpl)
				id = rpl.Id();
		}
		c.XX_Send(kind, arg, id);
	}

	static void Tell(int playerId, string title, string text)
	{
		SCR_PlayerControllerGroupComponent c = SCR_PlayerControllerGroupComponent.XX_GetFor(playerId);
		if (c)
			c.XX_Tell(title, text);
	}

	static IEntity FromRplId(RplId id)
	{
		if (!id.IsValid())
			return null;
		RplComponent rpl = RplComponent.Cast(Replication.FindItem(id));
		if (!rpl)
			return null;
		return rpl.GetEntity();
	}
}

class XX_Requests
{
	//! Solo servidor. Separa "quien" de "que": el autotest llama a HandleFor con un personaje simulado.
	static void Handle(int playerId, int kind, string arg, RplId sourceId)
	{
		if (!Replication.IsServer() || playerId < 0)
			return;
		IEntity player = GetGame().GetPlayerManager().GetPlayerControlledEntity(playerId);
		HandleFor(playerId, player, kind, arg, XX_Net.FromRplId(sourceId));
	}

	static void HandleFor(int playerId, IEntity player, int kind, string arg, IEntity source)
	{
		switch (kind)
		{
			case XX_EReq.STATUS: XX_Net.Tell(playerId, "Estado", "Todo en orden"); break;
		}
	}
}
```

- **Valida en el servidor:** distancia al vendedor, dinero y permisos. El cliente puede mentir.
- **Varios mods** pueden hacer `modded class` del mismo componente: se encadenan. Usa tu prefijo en todos los nombres.

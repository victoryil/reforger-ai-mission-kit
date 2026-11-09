// {{TITLE}} - gestor de la mision (vive en el GameMode). Autoridad: servidor.
//
// La mision es una lista de FASES en orden (BuildPhases). Cada fase tiene un tipo, un sitio y un texto.
// El servidor comprueba cada 2 s si la fase actual se ha cumplido; al cumplirse avisa a todos, guarda y pasa
// a la siguiente. Al acabar la ultima, victoria. Los clientes reciben fase, objetivo y posicion replicados.
//
// Para tu mision: cambia BuildPhases() (y los textos). Para tipos nuevos, anade un valor a {{P}}_EPhase,
// su arranque en StartPhase() y su comprobacion en IsPhaseDone().

enum {{P}}_EPhase
{
	REACH,      // llegar con algun jugador al sitio
	CLEAR,      // acabar con los grupos enemigos que aparecen en el sitio
	DESTROY,    // destruir el objeto que aparece en el sitio
	HOLD,       // aguantar X segundos con algun jugador en el sitio
	WAIT        // esperar X segundos (dialogo, transicion)
}

class {{P}}_Phase
{
	int m_eKind;
	string m_sTitle;       // titulo corto ("Asalto al puesto")
	string m_sObjective;   // lo que ve el jugador como objetivo
	string m_sStartText;   // aviso al empezar la fase
	string m_sDoneText;    // aviso al cumplirla
	vector m_vPos;
	float m_fRadius = 50;
	int m_iGroups = 2;     // CLEAR: grupos enemigos
	float m_fSeconds = 60; // HOLD / WAIT
	ResourceName m_sPrefab; // DESTROY: objeto a destruir

	static {{P}}_Phase Make(int kind, string title, string objective, vector pos)
	{
		{{P}}_Phase p = new {{P}}_Phase();
		p.m_eKind = kind;
		p.m_sTitle = title;
		p.m_sObjective = objective;
		p.m_vPos = pos;
		return p;
	}

	{{P}}_Phase Texts(string startText, string doneText)
	{
		m_sStartText = startText;
		m_sDoneText = doneText;
		return this;
	}
}

[ComponentEditorProps(category: "{{NAME}}", description: "Gestor de la mision {{TITLE}}")]
class {{P}}_MissionComponentClass : SCR_BaseGameModeComponentClass
{
}

class {{P}}_MissionComponent : SCR_BaseGameModeComponent
{
	static const string SAVE_DIR = "$profile:{{NAME}}";
	static const string SAVE_FILE = "$profile:{{NAME}}/partida.json";

	protected static {{P}}_MissionComponent s_Instance;

	// --- estado replicado (lo leen los clientes) ---
	[RplProp(onRplName: "OnClientStateChanged")]
	protected int m_iPhase = -1;
	[RplProp(onRplName: "OnClientStateChanged")]
	protected string m_sObjective;
	[RplProp()]
	protected vector m_vObjectivePos;
	[RplProp()]
	protected bool m_bFinished;

	// --- solo servidor ---
	protected ref array<ref {{P}}_Phase> m_aPhases = {};
	protected ref array<SCR_AIGroup> m_aGroups = {};
	protected IEntity m_Target;
	protected float m_fPhaseStart;
	protected float m_fHoldTime;
	protected int m_iMarker = -1;

	static {{P}}_MissionComponent GetInstance() { return s_Instance; }
	int GetPhase() { return m_iPhase; }
	int GetPhaseCount() { return m_aPhases.Count(); }
	string GetObjective() { return m_sObjective; }
	vector GetObjectivePos() { return m_vObjectivePos; }
	bool IsFinished() { return m_bFinished; }

	override void OnPostInit(IEntity owner)
	{
		super.OnPostInit(owner);
		s_Instance = this;
		if ({{P}}_ClientTest.IsEnabled() && !System.IsConsoleApp())
			{{P}}_ClientTest.Start();
	}

	override void OnGameModeStart()
	{
		super.OnGameModeStart();
		if (!Replication.IsServer())
			return;
		BuildPhases();
		int saved = Load();
		GetGame().GetCallqueue().CallLater(StartMission, 3000, false, saved);
		GetGame().GetCallqueue().CallLater(Tick, 2000, true);
		if ({{P}}_SelfTest.IsEnabled())
			GetGame().GetCallqueue().CallLater({{P}}_SelfTest.Run, 6000, false, this);
		if (System.IsCLIParam("{{P}}DumpMap"))
			GetGame().GetCallqueue().CallLater({{P}}_Util.DumpMap, 4000, false);
	}

	// ------------------------------------------------------------------ guion de la mision (EDITA AQUI)

	protected void BuildPhases()
	{
		m_aPhases.Clear();
		// Fase 1: llegar a un sitio
		m_aPhases.Insert({{P}}_Phase.Make({{P}}_EPhase.REACH, "Punto de reunion", "Id al punto de reunion", "{{PHASE1_POS}}")
			.Texts("Moveos al punto de reunion marcado en el mapa.", "Todos en posicion."));
		// Fase 2: limpiar un sitio de enemigos
		{{P}}_Phase clear = {{P}}_Phase.Make({{P}}_EPhase.CLEAR, "Asalto", "Acabad con el enemigo del objetivo", "{{PHASE2_POS}}")
			.Texts("El enemigo defiende el objetivo. Despejadlo.", "Zona despejada.");
		clear.m_iGroups = 2;
		m_aPhases.Insert(clear);
		// Fase 3: aguantar
		{{P}}_Phase hold = {{P}}_Phase.Make({{P}}_EPhase.HOLD, "Asegurar", "Mantened la posicion", "{{PHASE2_POS}}")
			.Texts("Mantened la posicion hasta que llegue el relevo.", "Relevo en camino. Mision cumplida.");
		hold.m_fSeconds = 60;
		m_aPhases.Insert(hold);
	}

	// ------------------------------------------------------------------ bucle del servidor

	protected void StartMission(int fromPhase)
	{
		StartPhase(Math.Clamp(fromPhase, 0, m_aPhases.Count() - 1));
	}

	protected void Tick()
	{
		if (m_bFinished || m_iPhase < 0 || m_iPhase >= m_aPhases.Count())
			return;
		// sin jugadores no avanza nada (salvo en el autotest)
		array<IEntity> players = {};
		{{P}}_Util.AlivePlayers(players);
		if (players.IsEmpty() && !{{P}}_SelfTest.IsEnabled())
			return;
		if (IsPhaseDone(m_aPhases[m_iPhase]))
			CompletePhase();
	}

	void StartPhase(int i)
	{
		if (i < 0 || i >= m_aPhases.Count())
			return;
		m_iPhase = i;
		{{P}}_Phase p = m_aPhases[i];
		m_fPhaseStart = {{P}}_Util.Now();
		m_fHoldTime = 0;
		CleanupPhase();
		switch (p.m_eKind)
		{
			case {{P}}_EPhase.CLEAR:
				for (int g = 0; g < p.m_iGroups; g++)
				{
					vector at = {{P}}_Util.RandomAround(p.m_vPos, 5, p.m_fRadius * 0.5);
					SCR_AIGroup grp = {{P}}_Util.SpawnGroup({{P}}_Prefabs.ENEMY_GROUP, at, {{P}}_Prefabs.WP_DEFEND, at);
					if (grp)
						m_aGroups.Insert(grp);
				}
				break;
			case {{P}}_EPhase.DESTROY:
				m_Target = {{P}}_Util.Spawn(p.m_sPrefab, {{P}}_Util.Ground(p.m_vPos), 0);
				break;
		}
		m_sObjective = p.m_sObjective;
		m_vObjectivePos = p.m_vPos;
		Replication.BumpMe();
		SetMarker(p);
		if (!p.m_sStartText.IsEmpty())
			Notify(p.m_sTitle, p.m_sStartText);
		Print(string.Format("[{{P}}] Fase %1/%2: %3", i + 1, m_aPhases.Count(), p.m_sTitle), LogLevel.NORMAL);
		Save();
	}

	protected bool IsPhaseDone({{P}}_Phase p)
	{
		switch (p.m_eKind)
		{
			case {{P}}_EPhase.REACH:
				return {{P}}_Util.AnyPlayerNear(p.m_vPos, p.m_fRadius);
			case {{P}}_EPhase.CLEAR:
			{
				// espera a que aparezcan antes de contar
				if ({{P}}_Util.Now() - m_fPhaseStart < 20)
					return false;
				int alive = 0;
				foreach (SCR_AIGroup g : m_aGroups)
					alive += {{P}}_Util.AliveInGroup(g);
				return alive == 0;
			}
			case {{P}}_EPhase.DESTROY:
				return !{{P}}_Util.IsAlive(m_Target);
			case {{P}}_EPhase.HOLD:
			{
				if ({{P}}_Util.AnyPlayerNear(p.m_vPos, p.m_fRadius))
					m_fHoldTime += 2;
				return m_fHoldTime >= p.m_fSeconds;
			}
			case {{P}}_EPhase.WAIT:
				return {{P}}_Util.Now() - m_fPhaseStart >= p.m_fSeconds;
		}
		return false;
	}

	void CompletePhase()
	{
		{{P}}_Phase p = m_aPhases[m_iPhase];
		if (!p.m_sDoneText.IsEmpty())
			Notify(p.m_sTitle, p.m_sDoneText);
		if (m_iPhase + 1 < m_aPhases.Count())
		{
			StartPhase(m_iPhase + 1);
			return;
		}
		Victory();
	}

	protected void Victory()
	{
		m_bFinished = true;
		m_sObjective = "Mision cumplida";
		Replication.BumpMe();
		RemoveMarker();
		Notify("{{TITLE}}", "Mision cumplida.");
		Print("[{{P}}] VICTORIA", LogLevel.NORMAL);
		Save();
		// fin de partida con la pantalla del juego (tras unos segundos para leer el aviso)
		GetGame().GetCallqueue().CallLater(EndGame, 15000, false);
	}

	protected void EndGame()
	{
		SCR_BaseGameMode gm = SCR_BaseGameMode.Cast(GetGame().GetGameMode());
		if (!gm)
			return;
		int factionIdx = -1;
		FactionManager fm = GetGame().GetFactionManager();
		if (fm)
			factionIdx = fm.GetFactionIndex(fm.GetFactionByKey({{P}}_SpawnLogic.PLAYER_FACTION));
		gm.EndGameMode(SCR_GameModeEndData.CreateSimple(EGameOverTypes.FACTION_VICTORY_SCORE, -1, factionIdx));
	}

	protected void CleanupPhase()
	{
		m_aGroups.Clear();
		m_Target = null;
	}

	// ------------------------------------------------------------------ marca del mapa (la ven todos)

	protected void SetMarker({{P}}_Phase p)
	{
		RemoveMarker();
		SCR_MapMarkerManagerComponent mm = SCR_MapMarkerManagerComponent.GetInstance();
		if (!mm)
			return;
		SCR_MapMarkerBase marker = new SCR_MapMarkerBase();
		marker.SetType(SCR_EMapMarkerType.PLACED_CUSTOM);
		marker.SetWorldPos(p.m_vPos[0], p.m_vPos[2]);
		marker.SetCustomText(p.m_sTitle);
		marker.SetIconEntry(1);
		marker.SetColorEntry(1);
		mm.InsertStaticMarker(marker, false, true);
		m_iMarker = marker.GetMarkerID();
	}

	protected void RemoveMarker()
	{
		if (m_iMarker < 0)
			return;
		SCR_MapMarkerManagerComponent mm = SCR_MapMarkerManagerComponent.GetInstance();
		if (mm)
		{
			SCR_MapMarkerBase m = mm.GetStaticMarkerByID(m_iMarker);
			if (m)
				mm.RemoveStaticMarker(m);
		}
		m_iMarker = -1;
	}

	// ------------------------------------------------------------------ avisos (servidor -> todos)

	void Notify(string title, string text)
	{
		Print(string.Format("[{{P}}] %1: %2", title, text), LogLevel.NORMAL);
		Rpc(RpcDo_Notify, title, text);
		if (!System.IsConsoleApp())
			RpcDo_Notify(title, text);   // partida alojada: el servidor tambien es jugador
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Broadcast)]
	protected void RpcDo_Notify(string title, string text)
	{
		SCR_HintManagerComponent.ShowCustomHint(text, title, 10);
	}

	//! En los clientes, cuando cambia la fase u objetivo replicados
	protected void OnClientStateChanged()
	{
		Print(string.Format("[{{P}}] (cliente) fase %1, objetivo: %2", m_iPhase + 1, m_sObjective), LogLevel.NORMAL);
	}

	// ------------------------------------------------------------------ guardado (fase actual)

	protected void Save()
	{
		if (!Replication.IsServer() || {{P}}_SelfTest.IsEnabled())
			return;
		FileIO.MakeDirectory(SAVE_DIR);
		JsonSaveContext ctx = new JsonSaveContext();
		ctx.WriteValue("version", 1);
		ctx.WriteValue("phase", m_iPhase);
		ctx.WriteValue("finished", m_bFinished);
		ctx.SaveToFile(SAVE_FILE);
	}

	protected int Load()
	{
		if ({{P}}_SelfTest.IsEnabled() || !FileIO.FileExists(SAVE_FILE))
			return 0;
		JsonLoadContext ctx = new JsonLoadContext();
		if (!ctx.LoadFromFile(SAVE_FILE))
			return 0;
		int phase;
		bool finished;
		ctx.ReadValue("phase", phase);
		ctx.ReadValue("finished", finished);
		if (finished)
			return 0;
		Print(string.Format("[{{P}}] Partida cargada en la fase %1", phase + 1), LogLevel.NORMAL);
		return phase;
	}

	// ------------------------------------------------------------------ para el autotest

	ref array<ref {{P}}_Phase> GetPhases() { return m_aPhases; }
	array<SCR_AIGroup> GetGroups() { return m_aGroups; }
	IEntity GetTarget() { return m_Target; }
	void ForceHold(float seconds) { m_fHoldTime += seconds; }
	void ForceTick() { Tick(); }
}

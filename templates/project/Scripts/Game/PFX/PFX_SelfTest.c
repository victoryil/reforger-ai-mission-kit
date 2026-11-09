// {{TITLE}} - autotest de SERVIDOR (parametro -{{SELFTEST_PARAM}}). Recorre la mision entera sin jugadores reales:
// crea un soldado "jugador simulado", cumple cada fase a la fuerza y comprueba que todo avanza.
// Cada comprobacion escribe "[{{P}}][TEST] OK: ..." o "[{{P}}][TEST] FALLO: ..." y al final "FIN del autotest".
// Lo lanza tools/server_test.py; lee el resumen con tools/logscan.py.

class {{P}}_SelfTest
{
	protected static {{P}}_MissionComponent s_Mission;
	protected static IEntity s_Fake;
	protected static int s_iErrors;
	protected static int s_iChecks;
	protected static int s_iLastPhase = -1;
	protected static int s_iSteps;
	protected static int s_iCheckedClear = -1;

	static bool IsEnabled()
	{
		return System.IsCLIParam("{{SELFTEST_PARAM}}");
	}

	static void Log(string s)
	{
		Print("[{{P}}][TEST] " + s, LogLevel.NORMAL);
	}

	static void Check(bool ok, string what)
	{
		s_iChecks++;
		if (ok)
		{
			Log("OK: " + what);
			return;
		}
		s_iErrors++;
		Print("[{{P}}][TEST] FALLO: " + what, LogLevel.ERROR);
	}

	static void Run({{P}}_MissionComponent mission)
	{
		s_Mission = mission;
		Log("INICIO del autotest");
		Check(mission.GetPhaseCount() > 0, string.Format("la mision tiene fases (%1)", mission.GetPhaseCount()));
		Check(GetGame().GetFactionManager().GetFactionByKey({{P}}_SpawnLogic.PLAYER_FACTION) != null, "existe la faccion del jugador " + {{P}}_SpawnLogic.PLAYER_FACTION);
		Check(GetGame().GetAIWorld() != null, "hay AIWorld en el mundo");
		Resource grp = Resource.Load({{P}}_Prefabs.ENEMY_GROUP);
		Check(grp && grp.IsValid(), "el prefab de grupo enemigo carga");
		GetGame().GetCallqueue().CallLater(Step, 3000, true);
	}

	//! Cada 3 s: cumple la fase actual a la fuerza y comprueba que pasa a la siguiente
	protected static void Step()
	{
		s_iSteps++;
		int phase = s_Mission.GetPhase();
		if (s_Mission.IsFinished())
		{
			Check(true, "la mision llega a la victoria");
			Finish();
			return;
		}
		if (s_iSteps > 60)
		{
			Check(false, string.Format("la mision se ha atascado en la fase %1", phase + 1));
			Finish();
			return;
		}
		if (phase < 0)
			return;
		if (phase != s_iLastPhase)
		{
			s_iLastPhase = phase;
			Check(!s_Mission.GetObjective().IsEmpty(), string.Format("fase %1 con objetivo: %2", phase + 1, s_Mission.GetObjective()));
		}
		{{P}}_Phase p = s_Mission.GetPhases()[phase];
		switch (p.m_eKind)
		{
			case {{P}}_EPhase.REACH:
			case {{P}}_EPhase.HOLD:
			{
				// el soldado simulado va al sitio
				if (!s_Fake)
					s_Fake = {{P}}_Util.Spawn("{{PLAYER_CHARACTER}}", {{P}}_Util.Ground(p.m_vPos), 0);
				if (s_Fake)
					s_Fake.SetOrigin({{P}}_Util.Ground(p.m_vPos));
				if (p.m_eKind == {{P}}_EPhase.HOLD)
					s_Mission.ForceHold(p.m_fSeconds);
				ForceComplete(p);
				break;
			}
			case {{P}}_EPhase.CLEAR:
			{
				int groups = s_Mission.GetGroups().Count();
				if (phase != s_iCheckedClear)
				{
					s_iCheckedClear = phase;
					Check(groups > 0, string.Format("aparecen los grupos enemigos (%1)", groups));
				}
				foreach (SCR_AIGroup g : s_Mission.GetGroups())
					KillGroup(g);
				break;
			}
			case {{P}}_EPhase.DESTROY:
			{
				Check(s_Mission.GetTarget() != null, "aparece el objetivo a destruir");
				if (s_Mission.GetTarget())
					SCR_EntityHelper.DeleteEntityAndChildren(s_Mission.GetTarget());
				break;
			}
		}
	}

	//! Las fases de "estar en el sitio" no cuentan al soldado simulado como jugador: se completan a mano
	protected static void ForceComplete({{P}}_Phase p)
	{
		s_Mission.CompletePhase();
	}

	protected static void KillGroup(SCR_AIGroup g)
	{
		if (!g)
			return;
		array<AIAgent> agents = {};
		g.GetAgents(agents);
		foreach (AIAgent a : agents)
		{
			IEntity e = a.GetControlledEntity();
			if (e)
				SCR_EntityHelper.DeleteEntityAndChildren(e);
		}
	}

	protected static void Finish()
	{
		GetGame().GetCallqueue().Remove(Step);
		Log(string.Format("FIN del autotest: %1 comprobaciones, %2 fallos", s_iChecks, s_iErrors));
	}
}

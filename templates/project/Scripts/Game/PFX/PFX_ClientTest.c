// {{TITLE}} - autotest de CLIENTE (parametro -{{CLIENTTEST_PARAM}} en el juego). Con un jugador real ya desplegado
// comprueba lo que llega por red y pide capturas en los momentos clave.
// Lo lanza: python tools/client_test.py --shots CAPTURA_JUEGO,CAPTURA_MAPA --until "FIN autotest de cliente"

class {{P}}_ClientTest
{
	protected static int s_iStage;
	protected static int s_iWait;
	protected static int s_iErrors;

	static bool IsEnabled()
	{
		return System.IsCLIParam("{{CLIENTTEST_PARAM}}");
	}

	static void Start()
	{
		Log("INICIO autotest de cliente");
		GetGame().GetCallqueue().CallLater(Tick, 2000, true);
	}

	protected static void Log(string s)
	{
		Print("[{{P}}][CLIENT] " + s, LogLevel.NORMAL);
	}

	protected static void Check(bool ok, string what)
	{
		if (ok)
		{
			Log("OK: " + what);
			return;
		}
		s_iErrors++;
		Print("[{{P}}][CLIENT] FALLO: " + what, LogLevel.ERROR);
	}

	protected static void Tick()
	{
		{{P}}_MissionComponent mission = {{P}}_MissionComponent.GetInstance();
		PlayerController pc = GetGame().GetPlayerController();
		if (!mission || !pc)
			return;
		IEntity me = pc.GetControlledEntity();
		s_iWait++;
		switch (s_iStage)
		{
			case 0:
			{
				if (!me || mission.GetObjective().IsEmpty())
				{
					if (s_iWait > 90)
					{
						Check(false, "el jugador no llega a desplegarse o no llega el objetivo");
						Finish();
					}
					return;
				}
				Check(true, "jugador desplegado en " + me.GetOrigin().ToString());
				Check(mission.GetPhase() >= 0, string.Format("llega la fase replicada (%1)", mission.GetPhase() + 1));
				Check(!mission.GetObjective().IsEmpty(), "llega el objetivo: " + mission.GetObjective());
				Log("CAPTURA_JUEGO");
				s_iStage = 1;
				s_iWait = 0;
				return;
			}
			case 1:
			{
				if (s_iWait < 3)
					return;
				GetGame().GetMenuManager().OpenMenu(ChimeraMenuPreset.MapMenu);
				s_iStage = 2;
				s_iWait = 0;
				return;
			}
			case 2:
			{
				if (s_iWait < 2)
					return;
				// centra el mapa en el objetivo actual para la captura
				SCR_MapEntity mapEnt = SCR_MapEntity.GetMapInstance();
				vector obj = mission.GetObjectivePos();
				if (mapEnt && obj != vector.Zero)
					mapEnt.ZoomPanSmooth(mapEnt.GetMinZoom() * 6, obj[0], obj[2], 0.1);
				s_iStage = 21;
				s_iWait = 0;
				return;
			}
			case 21:
			{
				if (s_iWait < 2)
					return;
				Log("CAPTURA_MAPA");
				s_iStage = 3;
				s_iWait = 0;
				return;
			}
			case 3:
			{
				if (s_iWait < 3)
					return;
				GetGame().GetMenuManager().CloseMenuByPreset(ChimeraMenuPreset.MapMenu);
				Finish();
				return;
			}
		}
	}

	protected static void Finish()
	{
		GetGame().GetCallqueue().Remove(Tick);
		if (s_iErrors == 0)
			Log("FIN autotest de cliente: todo correcto");
		else
			Log(string.Format("FIN autotest de cliente: %1 fallos", s_iErrors));
	}
}

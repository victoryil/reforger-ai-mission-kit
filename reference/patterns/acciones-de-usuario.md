# Acciones de usuario (mirar algo y pulsar F)

## Script

```c
class XX_TalkAction : ScriptedUserAction
{
	[Attribute("radio", desc: "Que menu abre")]
	protected string m_sMenu;

	// solo abre interfaz en quien la usa: no se envia por red
	override bool HasLocalEffectOnlyScript() { return true; }
	override bool CanBroadcastScript() { return false; }

	override bool GetActionNameScript(out string outName)
	{
		outName = "Hablar por radio";
		return true;
	}

	override bool CanBeShownScript(IEntity user)
	{
		return XX_Util.IsAlive(GetOwner());
	}

	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		// cliente: abre tu ventana o manda una peticion al servidor (ver red.md)
		XX_Net.Send(XX_EReq.STATUS, m_sMenu, pOwnerEntity);
	}
}
```

Para una acción que **cambia el mundo** (abrir una puerta, coger algo), no pongas `HasLocalEffectOnlyScript`. `PerformAction` corre en el servidor; haz el cambio allí.

## Prefab: añadir la acción a algo que ya existe

```
GenericEntity : "{GUID}Prefabs/Props/.../Radio.et" {
 ID "AAAAAAAAAAAAAAA1"
 components {
  ActionsManagerComponent "{GUID_DEL_COMPONENTE_EN_EL_PADRE}" {
   additionalActions {
    XX_TalkAction "{AAAAAAAAAAAAAAA2}" {
     ParentContextList {
      "default"
     }
     UIInfo UIInfo "{AAAAAAAAAAAAAAA3}" {
      Name "XX_TalkAction"
     }
     VisibilityRange 3
     Duration 0
     m_sMenu "radio"
    }
   }
  }
 }
}
```

- **Si el padre ya tiene `ActionsManagerComponent`:** usa su mismo GUID (`pakgrep.py "Radio.et"`).
- **Si no lo tiene:** añade `ActionsManagerComponent` con GUID nuevo y un `ActionContext` llamado `"default"` (copia uno de un prefab del juego con `pakgrep.py "ActionContext"`).
- **Personajes:** en los civiles del juego base, ese componente es `{520EA1D2F659CE02}` (probado).

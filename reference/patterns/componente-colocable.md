# Componente colocable en el editor (con dibujo en Workbench)

Útil para que el usuario coloque a mano en el World Editor puntos de la misión: objetivo, zona de aparición enemiga, extracción, garaje… Puede arrastrarlos y ajustar sus atributos, y ve un círculo con su radio.

```c
class XX_PointComponentClass : ScriptComponentClass
{
}

class XX_PointComponent : ScriptComponent
{
	[Attribute("", desc: "Identificador que usa el guion (p. ej. 'objetivo1')", category: "Mision")]
	string m_sId;

	[Attribute("50", UIWidgets.Slider, "Radio (m)", "5 500 5", category: "Mision")]
	float m_fRadius;

	protected static ref array<XX_PointComponent> s_aAll = {};

	override void OnPostInit(IEntity owner)
	{
		if (!s_aAll.Contains(this))
			s_aAll.Insert(this);
	}

	override void OnDelete(IEntity owner)
	{
		s_aAll.RemoveItem(this);
	}

	static XX_PointComponent Find(string id)
	{
		foreach (XX_PointComponent p : s_aAll)
		{
			if (p && p.m_sId == id)
				return p;
		}
		return null;
	}

	//! Solo en Workbench: dibuja el radio sobre el terreno
	override void _WB_AfterWorldUpdate(IEntity owner, float timeSlice)
	{
		int color = 0xFFE0A030;
		ShapeFlags f = ShapeFlags.ONCE | ShapeFlags.NOZBUFFER | ShapeFlags.TRANSP;
		vector c = owner.GetOrigin();
		vector ring[33];
		for (int i = 0; i <= 32; i++)
		{
			float a = i * Math.PI2 / 32;
			ring[i] = XX_Util.Ground(c + Vector(Math.Cos(a) * m_fRadius, 0, Math.Sin(a) * m_fRadius)) + "0 0.3 0";
		}
		Shape.CreateLines(color, f, ring, 33);
	}
}
```

- **Prefab:** hereda `GenericEntity` (o un prop pequeño) y añade `XX_PointComponent "{GUID}" { m_sId "objetivo1" m_fRadius 80 }`.
- **Capa:** varias instancias, cada una con su `m_sId`.
- **Guion:** busca `XX_PointComponent.Find("objetivo1").GetOwner().GetOrigin()`.
- **Los `static` sobreviven a «Reload Game»:** limpia `s_aAll` al iniciar si hace falta.

from fpdf import FPDF

MANUAL_CONTENT = {
    "es": {
        "title": "Centinela F2628 - Manual Operativo de Señales",
        "page_label": "Página",
        "logic_label": "Lógica",
        "description_label": "Descripción",
        "intro": (
            "Este documento detalla la lógica operativa del Centinela F2628 (v2026). "
            "Las señales han sido actualizadas para utilizar umbrales estadísticos adaptativos "
            "(Z-Score, Percentiles, Bandas de Bollinger) en lugar de valores fijos arbitrarios."
        ),
        "sections": [
            {
                "title": "1. SEÑALES CRÍTICAS (ROJO)",
                "items": [
                    {
                        "name": "COMBO_CRISIS (La Tormenta Perfecta)",
                        "logic": "Spread > 5.0% AND Spread_3d_Confirm AND SPX >= High50 AND RSI < High50_RSI AND VIX < 13",
                        "description": (
                            "La señal más peligrosa. Ocurre cuando el mercado de crédito se congela "
                            "(nadie presta, Spread > 5%) pero la bolsa sigue en máximos históricos con "
                            "complacencia extrema (VIX bajo). Es la divergencia final antes de un crash de liquidez."
                        ),
                    },
                    {
                        "name": "SOLVENCY_DEATH (Crisis de Solvencia)",
                        "logic": "Spread HY > 5.0% (confirmado por 3 días consecutivos)",
                        "description": (
                            "El diferencial (spread) entre bonos basura y bonos del tesoro supera el 5%. "
                            "Indica que los inversores exigen una prima de riesgo masiva porque temen una ola "
                            "de quiebras corporativas. El nivel del 5% es el estándar de la industria para definir "
                            "estrés crediticio sistémico."
                        ),
                    },
                    {
                        "name": "TEMPORAL_CRISIS (Convergencia Temporal)",
                        "logic": "(SUGAR_CRASH + EM_CURRENCY_STRESS en <30 días) OR (SOLVENCY_DEATH + WAR_PROTOCOL en <30 días)",
                        "description": (
                            "No es un evento único, sino una secuencia. Detecta cuando múltiples fracturas "
                            "estructurales ocurren en un periodo corto, indicando que el sistema no puede "
                            "contener las fugas por más tiempo."
                        ),
                    },
                    {
                        "name": "HOUSING_BUST (Giro del Ciclo Foldvary)",
                        "logic": "Housing_Starts_ZScore < -1.5 AND Mortgage_Rate > 52_Week_Avg",
                        "description": (
                            "El motor de la economía (construcción) se frena bruscamente (1.5 desviaciones estándar "
                            "por debajo de la media) MIENTRAS las tasas hipotecarias están en tendencia alcista "
                            "(superando su promedio anual). Esto confirma debilidad fundamental en el ciclo de tierras."
                        ),
                    },
                ],
            },
            {
                "title": "2. SEÑALES DE ALERTA (AMARILLO/NARANJA)",
                "items": [
                    {
                        "name": "BOND_FREEZE (Congelamiento de Bonos)",
                        "logic": "US10Y > Z_Score(Mean + 2*StdDev) AND RSI > 70",
                        "description": (
                            "Venta de pánico en el mercado de bonos del Tesoro. Los rendimientos se disparan "
                            "estadísticamente fuera de lo normal (2 desviaciones estándar), encareciendo toda "
                            "la deuda global."
                        ),
                    },
                    {
                        "name": "EM_CURRENCY_STRESS (Estrés Emergente)",
                        "logic": "DXY > Percentil_95 (1 año) AND US10Y > SMA_250",
                        "description": (
                            "El dólar alcanza niveles estadísticamente extremos (top 5% del último año) Y los bonos "
                            "del Tesoro (US10Y) están en tendencia alcista (sobre su media móvil de 250 días). "
                            "Esta combinación drena liquidez global y presiona la deuda de mercados emergentes."
                        ),
                    },
                    {
                        "name": "WAR_PROTOCOL (Protocolo de Guerra)",
                        "logic": "Oil > Z_Score(Mean + 2*StdDev) AND Gold > High20 AND SPX < Low20",
                        "description": (
                            "Shock geopolítico. El petróleo se dispara por miedo a cortes de suministro, el oro "
                            "sube como refugio, y las acciones caen. El mercado está descontando conflicto bélico."
                        ),
                    },
                    {
                        "name": "SUGAR_CRASH (Euforia Terminal)",
                        "logic": "SPX >= High50 AND RSI < High50_RSI (Divergencia) AND VIX < 13",
                        "description": (
                            "Una trampa alcista. El precio hace un nuevo máximo, pero la fuerza (RSI) es menor que antes, "
                            "y nadie compra protección (VIX bajo). El mercado está 'borracho' y vulnerable."
                        ),
                    },
                    {
                        "name": "LABOUR_SHOCK (Shock Laboral)",
                        "logic": "ICSA > Z_Score(Mean + 2*StdDev)",
                        "description": (
                            "Ruptura estadística en el empleo. Las solicitudes de desempleo se desvían más de 2 desviaciones "
                            "estándar de su media anual. Indica un cambio de régimen repentino en el mercado laboral."
                        ),
                    },
                ],
            },
            {
                "title": "3. SEÑALES DE TRADING (VERDE/SALIDA)",
                "items": [
                    {
                        "name": "BUY_BTC_NOW (Entrada Bitcoin)",
                        "logic": "Net_Liquidity > SMA(10) AND Prev_Net_Liq < SMA_Prev AND RSI < 60",
                        "description": (
                            "La Reserva Federal abre el grifo. La Liquidez Neta cruza al alza su media móvil, "
                            "indicando expansión monetaria. Históricamente, el mejor momento para comprar BTC."
                        ),
                    },
                    {
                        "name": "BUY_WPM_NOW (Entrada WPM)",
                        "logic": "Price < Bollinger_Lower_Band (Mean - 2*StdDev) AND RSI < 30 AND Volume > 2 * Avg_Vol",
                        "description": (
                            "Capitulación estadística. El precio rompe la banda de Bollinger inferior (2 sigmas), "
                            "confirmando que está barato con un 95% de confianza estadística, acompañado de pánico vendedor (volumen)."
                        ),
                    },
                ],
            },
        ],
        "output": "es-foldvarysignalmanual.pdf",
    },
    "en": {
        "title": "Centinela F2628 - Signal Operations Manual",
        "page_label": "Page",
        "logic_label": "Logic",
        "description_label": "Description",
        "intro": (
            "This document details the operating logic of Centinela F2628 (v2026). "
            "Signals have been updated to use adaptive statistical thresholds (Z-Score, Percentiles, "
            "Bollinger Bands) instead of arbitrary fixed values."
        ),
        "sections": [
            {
                "title": "1. CRITICAL SIGNALS (RED)",
                "items": [
                    {
                        "name": "COMBO_CRISIS (The Perfect Storm)",
                        "logic": "Spread > 5.0% AND Spread_3d_Confirm AND SPX >= High50 AND RSI < High50_RSI AND VIX < 13",
                        "description": (
                            "The most dangerous signal. It appears when the credit market freezes (no one lends, Spread > 5%) "
                            "while equities remain at historic highs with extreme complacency (low VIX). It is the final divergence "
                            "before a liquidity crash."
                        ),
                    },
                    {
                        "name": "SOLVENCY_DEATH (Solvency Crisis)",
                        "logic": "Spread HY > 5.0% (confirmed for 3 consecutive days)",
                        "description": (
                            "The spread between junk bonds and Treasuries exceeds 5%. It signals that investors demand a massive "
                            "risk premium because they fear a wave of corporate defaults. The 5% level is the industry standard for "
                            "systemic credit stress."
                        ),
                    },
                    {
                        "name": "TEMPORAL_CRISIS (Temporal Convergence)",
                        "logic": "(SUGAR_CRASH + EM_CURRENCY_STRESS within <30 days) OR (SOLVENCY_DEATH + WAR_PROTOCOL within <30 days)",
                        "description": (
                            "Not a single event, but a sequence. It detects when multiple structural fractures occur within a short "
                            "period, signalling the system cannot contain leaks much longer."
                        ),
                    },
                    {
                        "name": "HOUSING_BUST (Foldvary Cycle Turn)",
                        "logic": "Housing_Starts_ZScore < -1.5 AND Mortgage_Rate > 52_Week_Avg",
                        "description": (
                            "The engine of the economy (construction) slows sharply (1.5 standard deviations below the mean) "
                            "while mortgage rates trend higher (above the annual average). This confirms fundamental weakness in the land cycle."
                        ),
                    },
                ],
            },
            {
                "title": "2. WARNING SIGNALS (YELLOW/ORANGE)",
                "items": [
                    {
                        "name": "BOND_FREEZE (Bond Freeze)",
                        "logic": "US10Y > Z_Score(Mean + 2*StdDev) AND RSI > 70",
                        "description": (
                            "Panic selling in Treasuries. Yields spike statistically beyond normal (2 standard deviations), "
                            "raising the cost of global debt."
                        ),
                    },
                    {
                        "name": "EM_CURRENCY_STRESS (Emerging Market Stress)",
                        "logic": "DXY > Percentile_95 (1 year) AND US10Y > SMA_250",
                        "description": (
                            "The dollar reaches statistically extreme levels (top 5% of the past year) while US10Y is in an uptrend "
                            "(above its 250-day average). This combination drains global liquidity and pressures EM debt."
                        ),
                    },
                    {
                        "name": "WAR_PROTOCOL (War Protocol)",
                        "logic": "Oil > Z_Score(Mean + 2*StdDev) AND Gold > High20 AND SPX < Low20",
                        "description": (
                            "Geopolitical shock. Oil spikes on supply fears, gold rises as a refuge, and equities fall. The market is pricing conflict."
                        ),
                    },
                    {
                        "name": "SUGAR_CRASH (Terminal Euphoria)",
                        "logic": "SPX >= High50 AND RSI < High50_RSI (Divergence) AND VIX < 13",
                        "description": (
                            "A bull trap. Price makes a new high, but momentum (RSI) is weaker than before and no one buys protection (low VIX). "
                            "The market is overconfident and fragile."
                        ),
                    },
                    {
                        "name": "LABOUR_SHOCK (Labour Shock)",
                        "logic": "ICSA > Z_Score(Mean + 2*StdDev)",
                        "description": (
                            "Statistical break in employment. Jobless claims deviate by more than 2 standard deviations from the annual mean, "
                            "signalling a sudden regime change in labour conditions."
                        ),
                    },
                ],
            },
            {
                "title": "3. TRADING SIGNALS (GREEN/EXIT)",
                "items": [
                    {
                        "name": "BUY_BTC_NOW (Bitcoin Entry)",
                        "logic": "Net_Liquidity > SMA(10) AND Prev_Net_Liq < SMA_Prev AND RSI < 60",
                        "description": (
                            "The Federal Reserve opens the spigot. Net liquidity crosses above its moving average, indicating monetary expansion. "
                            "Historically, this has been the best entry point for BTC."
                        ),
                    },
                    {
                        "name": "BUY_WPM_NOW (WPM Entry)",
                        "logic": "Price < Bollinger_Lower_Band (Mean - 2*StdDev) AND RSI < 30 AND Volume > 2 * Avg_Vol",
                        "description": (
                            "Statistical capitulation. Price breaks the lower Bollinger Band (2 sigmas), confirming statistical cheapness with ~95% confidence, "
                            "paired with panic selling volume."
                        ),
                    },
                ],
            },
        ],
        "output": "en-foldvarysignalmanual.pdf",
    },
}


class PDF(FPDF):
    def __init__(self, title, page_label, logic_label, description_label):
        super().__init__()
        self.title_text = title
        self.page_label = page_label
        self.logic_label = logic_label
        self.description_label = description_label

    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.title_text, 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"{self.page_label} {self.page_no()}/{{nb}}", 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, label, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, logic, description):
        self.set_font('Courier', '', 10)
        self.set_text_color(100, 0, 0)
        self.multi_cell(0, 5, f"{self.logic_label}: {logic}")
        self.ln(2)

        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, f"{self.description_label}: {description}")
        self.ln(8)


def build_manual(lang_key):
    content = MANUAL_CONTENT[lang_key]
    pdf = PDF(
        content["title"],
        content["page_label"],
        content["logic_label"],
        content["description_label"],
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 5, content["intro"])
    pdf.ln(10)

    for section in content["sections"]:
        pdf.chapter_title(section["title"])
        for item in section["items"]:
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 6, item["name"], 0, 1)
            pdf.chapter_body(item["logic"], item["description"])

    pdf.output(content["output"])
    print(f"PDF generated successfully: {content['output']}")


if __name__ == "__main__":
    build_manual("es")
    build_manual("en")

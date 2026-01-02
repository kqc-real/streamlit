#!/usr/bin/env python3
"""
Heatmap-Generator für Deep Learning Fragenset
Zeigt Konzepte vs. kognitive Stufen mit intelligenter Label-Positionierung
"""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

def load_questions_data():
    """Lädt die Deep Learning Fragen-Daten"""
    file_path = Path("data/questions_Deep_Learning_Fundamentals.json")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def create_concept_cognitive_matrix():
    """Erstellt eine Matrix: Konzepte vs kognitive Stufen"""
    data = load_questions_data()

    # Sammle Daten für jedes Konzept und jede kognitive Stufe
    matrix_data = []

    for question in data['questions']:
        concept = question['concept']
        cognitive_level = question['cognitive_level']

        # Finde oder erstelle Eintrag
        existing_entry = None
        for entry in matrix_data:
            if entry['concept'] == concept and entry['cognitive_level'] == cognitive_level:
                existing_entry = entry
                break

        if existing_entry:
            existing_entry['count'] += 1
        else:
            matrix_data.append({
                'concept': concept,
                'cognitive_level': cognitive_level,
                'count': 1
            })

    return pd.DataFrame(matrix_data)

def calculate_text_positions(df, x_col, y_col):
    """Intelligente Label-Positionierung für nahe Punkte"""
    positions = []
    points = list(zip(df[x_col], df[y_col]))

    for i, (x1, y1) in enumerate(points):
        # Prüfe, ob dieser Punkt nahe bei anderen ist
        has_close_neighbors = False

        for j, (x2, y2) in enumerate(points):
            if i != j:
                # Distanzberechnung
                x_distance = abs(x1 - x2)
                y_distance = abs(y1 - y2)

                # Schwellenwert: nahe wenn x-Distanz <= 0.5 und y-Distanz <= 1
                if x_distance <= 0.5 and y_distance <= 1:
                    has_close_neighbors = True
                    break

        if has_close_neighbors:
            # Bei nahen Punkten: abwechselnd links/rechts
            positions.append("middle left" if i % 2 == 0 else "middle right")
        else:
            # Bei isolierten Punkten: Standard-Position rechts
            positions.append("middle right")

    return positions

def create_heatmap():
    """Erstellt die Heatmap mit intelligenter Label-Positionierung"""
    df = create_concept_cognitive_matrix()

    # Erstelle Pivot-Tabelle für Heatmap
    pivot_df = df.pivot_table(
        index='concept',
        columns='cognitive_level',
        values='count',
        fill_value=0
    )

    # Sortiere kognitive Stufen in logischer Reihenfolge
    cognitive_order = ['Reproduction', 'Application', 'Analysis']
    available_levels = [col for col in cognitive_order if col in pivot_df.columns]
    pivot_df = pivot_df[available_levels]

    # Erstelle Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='RdYlGn',
        text=pivot_df.values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>' +
                      'Kognitive Stufe: %{x}<br>' +
                      'Anzahl Fragen: %{z}<br>' +
                      '<extra></extra>'
    ))

    # Layout-Anpassungen
    fig.update_layout(
        title='Deep Learning Konzepte vs. Kognitive Stufen',
        xaxis_title='Kognitive Stufe',
        yaxis_title='Konzepte',
        height=800,
        width=1000,
        margin=dict(t=100, b=100, l=200, r=100),
        font_size=10
    )

    # Verbessere Achsen
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(tickangle=0)

    # Füge Colorbar hinzu
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Anzahl Fragen"
        )
    )

    return fig, pivot_df

def create_scatter_overlay():
    """Erstellt eine Scatter-Overlay für bessere Label-Positionierung"""
    df = create_concept_cognitive_matrix()

    # Map cognitive levels to numeric values for positioning
    level_mapping = {'Reproduction': 0, 'Application': 1, 'Analysis': 2}
    df['x_numeric'] = df['cognitive_level'].map(level_mapping)

    # Erstelle numerische y-Positionen für Konzepte
    unique_concepts = df['concept'].unique()
    concept_mapping = {concept: i for i, concept in enumerate(unique_concepts)}
    df['y_numeric'] = df['concept'].map(concept_mapping)

    # Berechne intelligente Textpositionen
    text_positions = calculate_text_positions(df, 'x_numeric', 'y_numeric')

    # Erstelle Scatter-Plot für Labels
    scatter_fig = go.Scatter(
        x=df['x_numeric'],
        y=df['y_numeric'],
        mode='text',
        text=df.apply(lambda r: f"{r['concept']}<br>({r['count']} Fragen)", axis=1),
        textposition=text_positions,
        textfont=dict(size=8, color='rgba(0,0,0,0.9)'),
        showlegend=False,
        hoverinfo='skip'
    )

    return scatter_fig, df

def main():
    """Hauptfunktion: Erstellt und speichert die Heatmap"""
    print("Erstelle Heatmap für Deep Learning Fragenset...")

    # Erstelle Heatmap
    heatmap_fig, pivot_df = create_heatmap()

    # Erstelle Scatter-Overlay für Labels
    scatter_trace, scatter_df = create_scatter_overlay()

    # Kombiniere Heatmap und Scatter
    combined_fig = go.Figure(data=[heatmap_fig.data[0], scatter_trace])

    # Kopiere Layout von Heatmap
    combined_fig.update_layout(heatmap_fig.layout)

    # Speichere als Bild
    output_path = "concept_cognitive_heatmap.png"
    combined_fig.write_image(output_path, scale=2)
    print(f"Heatmap gespeichert als: {output_path}")

    # Zeige auch die Daten
    print("\nDaten-Matrix:")
    print(pivot_df)

    # Zeige Verteilung
    print("\nVerteilung der Fragen:")
    total_questions = pivot_df.sum().sum()
    print(f"Gesamt: {total_questions} Fragen")

    for level in pivot_df.columns:
        level_total = pivot_df[level].sum()
        print(f"{level}: {level_total} Fragen ({level_total/total_questions*100:.1f}%)")

if __name__ == "__main__":
    main()
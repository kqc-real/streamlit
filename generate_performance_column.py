#!/usr/bin/env python3
"""
Erstelle eine vertikale Farbsäule mit Konzepten geordnet nach Performance
Rot = niedrige Performance, Grün = hohe Performance
"""

import pandas as pd
import plotly.graph_objects as go
from i18n.context import t as translate_ui
import streamlit as st

def _format_label_for_display(label: str, max_chars: int = 24) -> str:
    """Truncate long labels with an ellipsis for compact chart display."""
    if not label:
        return ""
    s = str(label).strip()
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 1] + "…"


def create_performance_column(questions):
    """Erstellt drei separate Säulen für MC-Test Status (Grün=richtig, Rot=falsch, Grau=nicht bearbeitet) basierend auf echten Fragen und Antworten"""
    
    # Sammle alle einzigartigen Konzepte aus den Fragen (für Concept-Performance)
    all_concepts = set()
    for question in questions:
        concept = question.get('concept')
        if concept:
            all_concepts.add(concept)
    
    if not all_concepts:
        return None  # Keine Konzepte vorhanden
    
    # Erstelle Performance-Daten pro Konzept basierend auf echten Antworten
    performance_data = []
    for concept in sorted(all_concepts):
        answered_count = 0
        correct_count = 0
        total = 0
        
        for i, question in enumerate(questions):
            if question.get('concept') == concept:
                total += 1
                answer_key = f"frage_{i}_beantwortet"
                if answer_key in st.session_state and st.session_state[answer_key] is not None:
                    answered_count += 1
                    if st.session_state[answer_key] > 0:
                        correct_count += 1
        
        coverage = answered_count / total if total else 0
        if answered_count == 0 or coverage <= 0.5:
            status = 'not_attempted'
            color = 'gray'
            status_text = translate_ui('app.status.not_attempted')
        elif correct_count / answered_count >= 0.8:
            # Höherer Schwellenwert, damit weniger als "understood" gelten
            status = 'correct'
            color = 'green'
            status_text = translate_ui('app.status.understood')
        else:
            status = 'incorrect'
            color = 'red'
            status_text = translate_ui('app.status.not_understood')
        
        performance_data.append({
            'concept': concept,
            'status': status,
            'color': color,
            'status_text': status_text,
            'answered': answered_count,
            'total': total
        })
    
    if not performance_data:
        return None
        
    df = pd.DataFrame(performance_data)

    # Positionen für die drei Säulen (breiter auseinander für Labels)
    column_positions = {'correct': -1.0, 'not_attempted': 0, 'incorrect': 1.0}
    column_colors = {'correct': 'green', 'not_attempted': 'gray', 'incorrect': 'red'}

    # Gruppiere nach Status und sortiere Konzepte alphabetisch innerhalb jeder Gruppe
    status_groups = df.groupby('status')
    sorted_groups = {}
    for status in ['correct', 'not_attempted', 'incorrect']:
        if status in status_groups.groups:
            group_df = status_groups.get_group(status)
            sorted_groups[status] = group_df.sort_values('concept', ascending=False)

    # Berechne individuelle Höhen für jede Säule basierend auf ihren Einträgen
    column_heights = {status: len(group) for status, group in sorted_groups.items()}

    # Erstelle Figur
    fig = go.Figure()

    # ZUERST: Füge alle Shapes hinzu (Hintergründe und Linien)
    # Füge farbige Hintergrundbereiche für jede Spalte hinzu
    pastel_colors = {'correct': 'rgba(144, 238, 144, 0.3)', 'not_attempted': 'rgba(211, 211, 211, 0.3)', 'incorrect': 'rgba(255, 182, 193, 0.3)'}
    
    spacing_factor = 1.1  # Noch mehr Abstand zwischen Punkten

    for status, pos in column_positions.items():
        height = column_heights.get(status, 0)
        if height > 0:  # Nur Hintergrund für Spalten mit Einträgen
            # Erstelle ein Rechteck mit abgerundeten Ecken als Pfad
            radius = 0.15  # Radius für abgerundete Ecken
            x0, x1 = pos - 0.4, pos + 0.4
            y0 = -0.5
            y1 = (height - 1) * spacing_factor + 1.0  # Mehr Kopfbereich

            # SVG-Pfad für Rechteck mit abgerundeten Ecken
            path = f"M {x0 + radius},{y0} L {x1 - radius},{y0} Q {x1},{y0} {x1},{y0 + radius} L {x1},{y1 - radius} Q {x1},{y1} {x1 - radius},{y1} L {x0 + radius},{y1} Q {x0},{y1} {x0},{y1 - radius} L {x0},{y0 + radius} Q {x0},{y0} {x0 + radius},{y0} Z"

            fig.add_shape(
                type="path",
                path=path,
                fillcolor=pastel_colors[status],
                line=dict(width=0),
                layer="below"
            )

    # DANN: Füge Kreise hinzu
    for status in ['correct', 'not_attempted', 'incorrect']:
        if status in sorted_groups:
            group_df = sorted_groups[status]

            # Verwende individuelle y-Positionen für jede Säule mit größerem Abstand
            y_pos = [i * spacing_factor for i in range(len(group_df))]
            display_labels = [_format_label_for_display(c) for c in group_df['concept'].tolist()]
            full_labels = group_df['concept'].tolist()

            fig.add_trace(go.Scatter(
                x=[column_positions[status]] * len(group_df),  # Säulen nebeneinander
                y=y_pos,  # Gleichmäßige vertikale Positionen
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=column_colors[status],
                    symbol='circle',
                    line=dict(width=0)  # Keine weißen Ränder
                ),
                text=display_labels,
                textposition="top center",
                textfont=dict(size=12, color='black'),
                hovertemplate='<b>%{customdata[3]}</b><br>' +
                              'Status: %{customdata[0]}<br>' +
                              'Antworten: %{customdata[1]}/%{customdata[2]}<br>' +
                              '<extra></extra>',
                customdata=pd.DataFrame({
                    "status_text": group_df["status_text"],
                    "answered": group_df["answered"],
                    "total": group_df["total"],
                    "concept_full": full_labels,
                }),
                showlegend=False,
                name=status
            ))

    # Layout für drei separate Säulen
    fig.update_layout(
        title='',
        xaxis=dict(
            showgrid=False,
            showticklabels=True,
            showline=False,  # Keine Achsenlinien
            zeroline=False,  # Keine Null-Linien
            range=[-1.5, 1.5],  # Mehr Platz für breitere Säulen
            title='',
            tickvals=[-1.0, 0, 1.0],
            ticktext=[
                translate_ui('app.status.understood'),
                translate_ui('app.status.not_attempted'),
                translate_ui('app.status.not_understood')
            ],
            tickfont=dict(size=14, weight='bold')  # Größer und fett
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            showline=False,  # Keine Achsenlinien
            zeroline=False,  # Keine Null-Linien
            range=[-0.5, max(column_heights.values()) * spacing_factor + 0.7],  # Mehr Platz für Labels
            title='',
        ),
        height=max(560, int(max(column_heights.values()) * 54)),  # Noch mehr vertikaler Platz pro Element
        width=1200,  # Breiter für mehr Label-Platz
        margin=dict(t=20, b=50, l=100, r=100),  # Minimaler oberer Rand
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent
    )

    return fig

#!/usr/bin/env python3
"""
Erstellt eine 2D-Heatmap: Topics × Cognitive Levels
Zeigt Performance-% mit Farbcodierung und Anzahl bearbeiteter Fragen
"""

import pandas as pd
import plotly.graph_objects as go
from i18n.context import t as translate_ui
import streamlit as st


def create_difficulty_heatmap(questions):
    """
    Erstellt eine Heatmap: Topics (Y-Achse) × Cognitive Levels (X-Achse)
    Zeigt Performance in % und Anzahl Fragen pro Zelle
    """
    
    # Sammle alle einzigartigen Topics und Cognitive Levels
    topics = set()
    cognitive_levels_set = set()
    
    for question in questions:
        topic = question.get('thema', 'Allgemein')
        cog_level = question.get('cognitive_level', 'Unknown')
        if topic:
            topics.add(topic)
        if cog_level:
            cognitive_levels_set.add(cog_level)
    
    if not topics or not cognitive_levels_set:
        return None
    
    # Definiere die Reihenfolge der Cognitive Levels (Bloom-Hierarchie)
    level_order = {
        'Reproduction': 0,
        'Application': 1,
        'Analysis': 2
    }
    
    cognitive_levels = sorted(
        [level for level in cognitive_levels_set if level in level_order],
        key=lambda x: level_order.get(x, 999)
    )
    
    if not cognitive_levels:
        return None
    
    topics_sorted = sorted(topics)
    
    # Erstelle Matrix für Performance und Counts
    matrix_performance = []
    matrix_counts = []
    matrix_unanswered = []  # Tracking für unbeantwortete Fragen
    matrix_hover = []
    
    for topic in topics_sorted:
        row_perf = []
        row_count = []
        row_unanswered = []
        row_hover = []
        
        for cog_level in cognitive_levels:
            # Finde alle Fragen für dieses Topic × Cognitive Level
            relevant_questions = [
                (i, q) for i, q in enumerate(questions)
                if q.get('thema', 'Allgemein') == topic 
                and q.get('cognitive_level') == cog_level
            ]
            
            if not relevant_questions:
                row_perf.append(None)  # Keine Daten
                row_unanswered.append(0)
                row_count.append(0)
                row_hover.append(f"{topic}<br>{translate_ui('app.cognitive.' + cog_level.lower(), default=cog_level)}<br>{translate_ui('heatmap.no_data', default='Keine Fragen')}")
                continue
            
            # Berechne Performance für diese Zelle
            total_points = 0
            max_points = 0
            answered_count = 0
            unanswered_count = 0
            
            for i, question in relevant_questions:
                gewichtung = question.get('gewichtung', 1)
                max_points += gewichtung
                
                answer_key = f"frage_{i}_beantwortet"
                if answer_key in st.session_state and st.session_state[answer_key] is not None:
                    answered_count += 1
                    points = max(0, st.session_state[answer_key])  # Nur positive Punkte
                    total_points += points
                else:
                    unanswered_count += 1
            
            if answered_count == 0:
                # Fragen existieren, aber nicht beantwortet
                row_perf.append(None)
                row_unanswered.append(len(relevant_questions))
                row_count.append(len(relevant_questions))
                row_hover.append(
                    f"{topic}<br>"
                    f"{translate_ui('app.cognitive.' + cog_level.lower(), default=cog_level)}<br>"
                    f"{translate_ui('heatmap.unanswered', default='Unbeantwortet')}: {len(relevant_questions)}"
                )
            else:
                # Berechne Performance-Prozentsatz über ALLE Fragen (unbeantwortete = 0 Punkte)
                performance_pct = (total_points / max_points * 100) if max_points > 0 else 0
                row_unanswered.append(unanswered_count)
                row_perf.append(performance_pct)
                row_count.append(len(relevant_questions))
                
                # Hover mit vollständiger Info
                hover_text = (
                    f"{topic}<br>"
                    f"{translate_ui('app.cognitive.' + cog_level.lower(), default=cog_level)}<br>"
                    f"{translate_ui('heatmap.performance', default='Performance')}: {performance_pct:.1f}%<br>"
                    f"{translate_ui('heatmap.answered', default='Beantwortet')}: {answered_count}/{len(relevant_questions)}"
                )
                if unanswered_count > 0:
                    hover_text += f"<br>{translate_ui('heatmap.unanswered', default='Unbeantwortet')}: {unanswered_count}"
                row_hover.append(hover_text)
        
        matrix_unanswered.append(row_unanswered)
        matrix_performance.append(row_perf)
        matrix_counts.append(row_count)
        matrix_hover.append(row_hover)
    
    # Übersetze Cognitive Level Labels
    cognitive_level_labels = [
        translate_ui('app.cognitive.' + level.lower(), default=level)
        for level in cognitive_levels
    ]
    
    # Erstelle Heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix_performance,
        x=cognitive_level_labels,
        y=topics_sorted,
        colorscale=[
            [0.0, 'rgb(220, 38, 38)'],    # Rot (0%)
            [0.5, 'rgb(251, 191, 36)'],   # Gelb (50%)
            [1.0, 'rgb(34, 197, 94)']     # Grün (100%)
        ],
        zmid=50,  # Mittelpunkt bei 50%
        zmin=0,
        zmax=100,
        connectgaps=False,  # Keine Interpolation zwischen Zellen
        hovertemplate='%{customdata}<extra></extra>',
        customdata=matrix_hover,
        colorbar=dict(
            title=translate_ui('heatmap.colorbar_title', default='Performance (%)'),
            ticksuffix='%',
            thickness=20,
            len=0.7
        ),
        # Graue Farbe für None-Werte (unbeantwortete Fragen)
        xgap=2,
        ygap=2
    ))
    
    # Füge Annotations für Fragenanzahl hinzu (nur bei Zellen mit Daten)
    annotations = []
    for i, topic in enumerate(topics_sorted):
        for j, cog_level in enumerate(cognitive_levels):
            count = matrix_counts[i][j]
            unanswered = matrix_unanswered[i][j]
            performance = matrix_performance[i][j]
            
            if count > 0:
                # Zeige immer Anzahl beantwortet/gesamt
                answered = count - unanswered
                text = f"n={answered}/{count}"
                
                # Weiße Schrift auf allen farbigen Hintergründen
                if performance is None:
                    # Komplett unbeantwortet (grau)
                    text_color = 'rgba(0,0,0,0.7)'
                else:
                    # Alle Performance-Werte haben farbigen Hintergrund → weiße Schrift
                    text_color = 'white'
                
                annotations.append(
                    dict(
                        x=cognitive_level_labels[j],
                        y=topic,
                        text=text,
                        showarrow=False,
                        font=dict(size=10, color=text_color, weight='bold' if unanswered > 0 else 'normal')
                    )
                )
    
    # Füge graue Rechtecke für unbeantwortete Zellen hinzu
    shapes = []
    for i, topic in enumerate(topics_sorted):
        for j, cog_level in enumerate(cognitive_levels):
            if matrix_performance[i][j] is None and matrix_counts[i][j] > 0:
                # Graues Rechteck für komplett unbeantwortete Fragen
                shapes.append(dict(
                    type='rect',
                    xref='x',
                    yref='y',
                    x0=j - 0.5,
                    x1=j + 0.5,
                    y0=i - 0.5,
                    y1=i + 0.5,
                    fillcolor='rgba(200, 200, 200, 0.5)',
                    line=dict(width=0)
                ))
    
    fig.update_layout(
        title='',
        xaxis=dict(
            title=translate_ui('heatmap.xaxis_title', default='Kognitive Stufe'),
            side='bottom',
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title=translate_ui('heatmap.yaxis_title', default='Thema'),
            tickfont=dict(size=11),
            autorange='reversed'  # Topics von oben nach unten
        ),
        shapes=shapes,
        height=max(400, len(topics_sorted) * 60),  # Dynamische Höhe
        width=800,
        margin=dict(t=20, b=80, l=150, r=100),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        annotations=annotations
    )
    
    return fig

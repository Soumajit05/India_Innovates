"""
Temporal trend analysis and forecasting.
Detects patterns, anomalies, and forecasts in time-series graph data.
"""
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import json

logger = logging.getLogger(__name__)

try:
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available; statistical trending disabled")


class TemporalTrendAnalyzer:
    """Analyzes time-series trends in graph metrics."""
    
    def __init__(self, window_size: int = 7):
        """
        Initialize analyzer.
        
        Args:
            window_size: Days for moving average calculation
        """
        self.window_size = window_size
    
    def compute_trend(self, values: List[Tuple[datetime, float]]) -> Dict:
        """
        Compute trend direction and velocity.
        
        Args:
            values: List of (timestamp, value) tuples
            
        Returns:
            Dict with trend_direction, velocity, strength
        """
        if len(values) < 2:
            return {"trend": "insufficient_data", "velocity": 0, "strength": 0}
        
        # Sort by timestamp
        values = sorted(values, key=lambda x: x[0])
        timestamps = [v[0] for v in values]
        data_points = [v[1] for v in values]
        
        # Calculate time deltas (in days)
        time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() / 86400 
                      for i in range(len(timestamps)-1)]
        avg_interval = statistics.mean(time_diffs) if time_diffs else 1
        
        # Simple linear regression
        n = len(data_points)
        if n < 2:
            return {"trend": "insufficient_data", "velocity": 0, "strength": 0}
        
        # Use indices for X (0, 1, 2, ...) and scale by actual time intervals
        x = list(range(n))
        y = data_points
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # Trend direction
        velocity = slope
        if abs(velocity) < 0.01:
            trend = "stable"
        elif velocity > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Strength (R-squared)
        try:
            y_pred = [slope * xi + (mean_y - slope * mean_x) for xi in x]
            ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
            ss_tot = sum((y[i] - mean_y) ** 2 for i in range(n))
            strength = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        except:
            strength = 0
        
        return {
            "trend": trend,
            "velocity": velocity,
            "strength": max(0, min(1, strength)),  # Clamp to [0, 1]
            "recent_avg": statistics.mean(data_points[-3:]) if len(data_points) >= 3 else data_points[-1],
            "historical_avg": statistics.mean(data_points),
            "volatility": statistics.stdev(data_points) if len(data_points) > 1 else 0
        }
    
    def detect_anomalies(self, values: List[Tuple[datetime, float]], z_threshold: float = 2.5) -> List[int]:
        """
        Detect outlier data points using Z-score.
        
        Args:
            values: Sorted list of (timestamp, value) tuples
            z_threshold: Z-score threshold (>2.5 = 99th percentile)
            
        Returns:
            Indices of anomalous values
        """
        if len(values) < 3:
            return []
        
        values = sorted(values, key=lambda x: x[0])
        data_points = [v[1] for v in values]
        
        mean = statistics.mean(data_points)
        stdev = statistics.stdev(data_points) if len(data_points) > 1 else 1
        
        if stdev == 0:
            return []
        
        anomalies = []
        for i, point in enumerate(data_points):
            z_score = abs((point - mean) / stdev)
            if z_score > z_threshold:
                anomalies.append(i)
        
        return anomalies
    
    def compute_moving_average(
        self,
        values: List[Tuple[datetime, float]],
        window: int = None
    ) -> List[Tuple[datetime, float]]:
        """
        Compute moving average.
        
        Args:
            values: Sorted time-series values
            window: Window size (days)
            
        Returns:
            Smoothed values
        """
        if window is None:
            window = self.window_size
        
        if len(values) < window:
            return values
        
        values = sorted(values, key=lambda x: x[0])
        smoothed = []
        
        for i in range(len(values)):
            # Take values within window
            window_start = values[i][0] - timedelta(days=window)
            window_values = [v[1] for v in values if window_start <= v[0] <= values[i][0]]
            
            if window_values:
                smoothed.append((values[i][0], statistics.mean(window_values)))
        
        return smoothed
    
    def forecast(
        self,
        values: List[Tuple[datetime, float]],
        days_ahead: int = 7,
        method: str = "linear"
    ) -> List[Tuple[datetime, float, float]]:
        """
        Simple forecasting (linear extrapolation).
        
        Args:
            values: Historical time-series
            days_ahead: Number of days to forecast
            method: Forecasting method ("linear", "exponential_smoothing")
            
        Returns:
            List of (timestamp, forecast_value, confidence_interval) tuples
        """
        if len(values) < 2:
            return []
        
        values = sorted(values, key=lambda x: x[0])
        trend_info = self.compute_trend(values)
        
        if trend_info["trend"] == "insufficient_data":
            return []
        
        last_date = values[-1][0]
        last_value = values[-1][1]
        slope = trend_info["velocity"]
        volatility = trend_info["volatility"]
        
        forecasts = []
        for days_offset in range(1, days_ahead + 1):
            forecast_date = last_date + timedelta(days=days_offset)
            
            # Linear extrapolation
            forecast_value = last_value + (slope * days_offset)
            
            # Confidence interval widens into future
            ci_width = volatility * (1 + days_offset / 10)
            
            forecasts.append({
                "date": forecast_date.isoformat(),
                "forecast": forecast_value,
                "ci_lower": forecast_value - ci_width,
                "ci_upper": forecast_value + ci_width,
                "confidence": max(0.5, 1.0 - (days_offset / days_ahead) * 0.3)  # Decreases over time
            })
        
        return forecasts


class GraphMetricsTimeSeries:
    """Tracks time-series metrics for the knowledge graph."""
    
    def __init__(self):
        """Initialize metrics storage."""
        self.metrics = defaultdict(list)  # metric_name -> [(timestamp, value)]
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """
        Record metric value at timestamp.
        
        Args:
            metric_name: Name of metric (e.g., "edges_per_domain.GEOPOLITICS")
            value: Metric value
            timestamp: Timestamp (default: now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.metrics[metric_name].append((timestamp, value))
    
    def get_metrics_summary(self, metric_name: str, days: int = 7) -> Dict:
        """
        Get summary statistics for metric over past N days.
        
        Args:
            metric_name: Metric to analyze
            days: Historical window in days
            
        Returns:
            Summary with trend, anomalies, forecast
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_values = [(t, v) for t, v in self.metrics.get(metric_name, []) if t >= cutoff_date]
        
        if not recent_values:
            return {"status": "insufficient_data"}
        
        analyzer = TemporalTrendAnalyzer()
        trend = analyzer.compute_trend(recent_values)
        anomalies_idx = analyzer.detect_anomalies(recent_values)
        forecast = analyzer.forecast(recent_values, days_ahead=7)
        
        anomaly_dates = [recent_values[i][0].isoformat() for i in anomalies_idx if i < len(recent_values)]
        
        return {
            "metric": metric_name,
            "period_days": days,
            "data_points": len(recent_values),
            "trend": trend,
            "anomalies": anomaly_dates,
            "forecast": forecast,
            "current_value": recent_values[-1][1] if recent_values else None
        }
    
    def export_metrics(self, metric_names: List[str] = None) -> Dict:
        """Export metrics as JSON."""
        if metric_names is None:
            metric_names = list(self.metrics.keys())
        
        result = {}
        for name in metric_names:
            if name in self.metrics:
                result[name] = [
                    {"timestamp": t.isoformat(), "value": v}
                    for t, v in self.metrics[name]
                ]
        
        return result


# Global metrics instance
graph_metrics_ts = GraphMetricsTimeSeries()

#!/usr/bin/env python3
"""
Analyze A/B Test Results for Hook Variants
Calculates conversion rate (registration rate) by hook variant (A vs B)
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def analyze_hook_ab_test():
    """Analyze registration rates by hook variant"""
    
    analytics_dir = 'analytics'
    
    # Collect all data
    all_data = []
    
    if os.path.exists(analytics_dir):
        for filename in os.listdir(analytics_dir):
            if filename.startswith('visits-') and filename.endswith('.json'):
                filepath = os.path.join(analytics_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        all_data.extend(data)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    # Organize data by hook variant
    variant_stats = defaultdict(lambda: {
        'total_visits': 0,
        'registrations': 0,
        'unique_visitors': set(),
        'unique_registrants': set(),
        'visitor_names': [],
        'page_views': defaultdict(int)
    })
    
    # Process all events
    for event in all_data:
        hook_variant = event.get('hookVariant', 'Unknown')
        visitor_id = event.get('visitorId')
        session_id = event.get('sessionId')
        event_type = event.get('event', 'page_visit')
        page = event.get('page', 'unknown')
        name = event.get('name')
        email = event.get('email')
        
        # Track by variant
        if hook_variant in ['A', 'B']:
            stats = variant_stats[hook_variant]
            
            # Count page visits
            if event_type == 'page_visit':
                stats['total_visits'] += 1
                if visitor_id:
                    stats['unique_visitors'].add(visitor_id)
                stats['page_views'][page] += 1
            
            # Count registrations
            if event_type == 'registration' or (event_type == 'page_visit' and email):
                stats['registrations'] += 1
                if visitor_id:
                    stats['unique_registrants'].add(visitor_id)
                if name:
                    stats['visitor_names'].append(name)
    
    # Calculate conversion rates
    print("\n" + "="*70)
    print("HOOK VARIANT A/B TEST ANALYSIS")
    print("="*70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not variant_stats:
        print("No data available yet. Check back once visitors have been tracked.")
        return
    
    # Display results for each variant
    results = []
    for variant in sorted(variant_stats.keys()):
        stats = variant_stats[variant]
        
        total_visits = stats['total_visits']
        registrations = stats['registrations']
        unique_visitors = len(stats['unique_visitors'])
        unique_registrants = len(stats['unique_registrants'])
        
        # Calculate conversion rates
        conversion_rate = (registrations / total_visits * 100) if total_visits > 0 else 0
        visitor_conversion = (unique_registrants / unique_visitors * 100) if unique_visitors > 0 else 0
        
        results.append({
            'variant': variant,
            'total_visits': total_visits,
            'registrations': registrations,
            'unique_visitors': unique_visitors,
            'unique_registrants': unique_registrants,
            'conversion_rate': conversion_rate,
            'visitor_conversion': visitor_conversion,
            'visitor_names': stats['visitor_names'],
            'page_views': stats['page_views']
        })
    
    # Print results table
    print(f"{'Variant':<10} {'Visits':<10} {'Registrations':<15} {'Conv. Rate':<12} {'Unique Visitors':<18} {'Visitor Conv.':<15}")
    print("-" * 90)
    
    for result in sorted(results, key=lambda x: x['variant']):
        print(f"Variant {result['variant']:<3} {result['total_visits']:<10} {result['registrations']:<15} {result['conversion_rate']:>10.1f}% {result['unique_visitors']:<18} {result['visitor_conversion']:>13.1f}%")
    
    # Show registrants by variant
    print("\n" + "="*70)
    print("REGISTRANTS BY VARIANT")
    print("="*70)
    
    for result in sorted(results, key=lambda x: x['variant']):
        print(f"\nVariant {result['variant']}: {len(result['visitor_names'])} registrations")
        if result['visitor_names']:
            for name in sorted(set(result['visitor_names'])):
                print(f"  ✓ {name}")
        else:
            print("  (No registrants yet)")
    
    # Show page views by variant
    print("\n" + "="*70)
    print("PAGE VIEWS BY VARIANT")
    print("="*70)
    
    for result in sorted(results, key=lambda x: x['variant']):
        print(f"\nVariant {result['variant']}:")
        for page, count in sorted(result['page_views'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {page}: {count} views")
    
    # Winner determination
    print("\n" + "="*70)
    print("PRELIMINARY WINNER")
    print("="*70)
    
    if len(results) >= 2:
        sorted_results = sorted(results, key=lambda x: x['conversion_rate'], reverse=True)
        winner = sorted_results[0]
        runner_up = sorted_results[1]
        
        difference = winner['conversion_rate'] - runner_up['conversion_rate']
        
        print(f"\n🏆 Variant {winner['variant']} is performing better!")
        print(f"   Conversion Rate: {winner['conversion_rate']:.1f}% vs {runner_up['conversion_rate']:.1f}%")
        print(f"   Difference: +{difference:.1f} percentage points")
        
        if winner['registrations'] >= 10:
            print(f"\n✓ Sample size is adequate ({winner['registrations']} registrations)")
        else:
            print(f"\n⚠️  Sample size may be too small ({winner['registrations']} registrations) - continue testing")
    
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    analyze_hook_ab_test()

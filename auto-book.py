#!/usr/bin/env python3
"""
BarberApp Auto-Booking Monitor

Monitora gli slot disponibili e prenota automaticamente al primo disponibile.

Uso:
    python auto_book.py --service 10 --barber Giovanni --interval 300
    python auto_book.py --service 10 --barber Giovanni --min-hour 9 --max-hour 13
"""

import argparse
import time
import sys
import requests as http_requests
from datetime import datetime

from config import BARBER_ID, USERNAME, PASSWORD, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from barberapp_client import BarberAppClient

from rich.console import Console
from rich.panel import Panel

console = Console()


def send_telegram(message: str) -> bool:
    """
    Invia notifica Telegram se configurato.
    
    Returns:
        True se inviato con successo o se non configurato
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return True  # Non configurato, skip silenzioso
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        response = http_requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
        return response.status_code == 200
    except Exception as e:
        console.print(f"[red]⚠️ Errore Telegram: {e}[/red]")
        return False


def monitor_and_book(
    service_id: int,
    barber: str,
    interval: int = 300,
    min_hour: int = 0,
    max_hour: int = 24,
    dry_run: bool = False
):
    """
    Monitora slot disponibili e prenota automaticamente.
    
    Args:
        service_id: ID del servizio da prenotare
        barber: Nome del barbiere
        interval: Intervallo di controllo in secondi (default 5 min)
        min_hour: Ora minima preferita (es. 9 = dalle 9:00)
        max_hour: Ora massima preferita (es. 13 = fino alle 13:00)
        dry_run: Se True, non prenota effettivamente
    """
    client = BarberAppClient(
        user_id=BARBER_ID,
        username=USERNAME,
        password=PASSWORD
    )
    
    service_name = client.get_service_name(service_id)
    duration = client.get_service_duration(barber, service_id)
    
    # Header
    time_filter = ""
    if min_hour and max_hour:
        time_filter = f" (ore {min_hour}:00 - {max_hour}:00)"
    elif min_hour:
        time_filter = f" (dalle {min_hour}:00)"
    elif max_hour:
        time_filter = f" (fino alle {max_hour}:00)"
    
    console.print(Panel(
        f"[bold]🤖 AUTO-BOOKING MONITOR[/bold]\n\n"
        f"[cyan]Servizio:[/cyan] [{service_id}] {service_name} ({duration}min)\n"
        f"[cyan]Barbiere:[/cyan] {barber}\n"
        f"[cyan]Controllo ogni:[/cyan] {interval} secondi\n"
        f"[cyan]Filtro orario:[/cyan]{time_filter or ' Nessuno'}\n"
        f"[cyan]Telegram:[/cyan] {'✅ Attivo' if TELEGRAM_BOT_TOKEN else '❌ Non configurato'}",
        title="⏰ Monitoraggio Attivo",
    ))
    
    console.print("\n[dim]Premi Ctrl+C per interrompere...[/dim]\n")
    
    check_count = 0
    
    try:
        while True:
            check_count += 1
            now = datetime.now()
            console.print(f"[dim][{now.strftime('%H:%M:%S')}] Check #{check_count}...[/dim]", end=" ")
            
            # Refresh cache
            client._schedule = None
            
            # Cerca slot disponibili
            days = client.get_available_slots_for_barber(barber)
            
            found_slot = None
            
            for day in days:
                date_str = day['Gi']
                slots = client.calculate_available_slots(date_str, barber, service_id)
                
                for time_str, slot_duration in slots:
                    hour = int(time_str[:2])
                    
                    # Applica filtro orario
                    if min_hour and hour < min_hour:
                        continue
                    if max_hour and hour >= max_hour:
                        continue
                    
                    # Trovato slot valido!
                    date = client.parse_date(date_str)
                    found_slot = {
                        'date_str': date_str,
                        'date': date,
                        'time': time_str,
                        'datetime_str': date_str + time_str.replace(":", "")
                    }
                    break
                
                if found_slot:
                    break
            
            if found_slot:
                day_name = ['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'][found_slot['date'].weekday()]
                console.print("[bold green]✅ TROVATO![/bold green]")
                console.print("\n[bold]🎯 Slot disponibile:[/bold]")
                console.print(f"   📅 {day_name} {found_slot['date'].strftime('%d/%m/%Y')}")
                console.print(f"   🕐 {found_slot['time']}")
                console.print(f"   ✂️  {service_name}")
                console.print(f"   💇 {barber}")
                
                if dry_run:
                    console.print("\n[yellow]⚠️  DRY RUN - Prenotazione non effettuata[/yellow]")
                    # Notifica Telegram
                    send_telegram(
                        f"🔔 <b>@Trifase Slot Disponibile!</b>\n\n"
                        f"📅 {day_name} {found_slot['date'].strftime('%d/%m/%Y')}\n"
                        f"🕐 {found_slot['time']}\n"
                        f"✂️ {service_name}\n"
                        f"💇 {barber}\n\n"
                        f"⚠️ <i>Dry run - non prenotato</i>"
                    )
                    return True
                
                # Prenota!
                console.print("\n[cyan]📤 Invio prenotazione...[/cyan]")
                success = client.book(found_slot['datetime_str'], service_id, barber)
                
                if success:
                    console.print("[bold green]🎉 PRENOTAZIONE EFFETTUATA![/bold green]")
                    console.print(f"\n   Riepilogo: {day_name} {found_slot['date'].strftime('%d/%m/%Y')} alle {found_slot['time']}")
                    # Notifica Telegram
                    send_telegram(
                        f"✅ <b>@Trifase Prenotazione Effettuata!</b>\n\n"
                        f"📅 {day_name} {found_slot['date'].strftime('%d/%m/%Y')}\n"
                        f"🕐 {found_slot['time']}\n"
                        f"✂️ {service_name}\n"
                        f"💇 {barber}"
                    )
                    return True
                else:
                    console.print("[red]❌ Errore - slot non più disponibile, riprovo...[/red]")
            else:
                console.print("[yellow]Nessuno slot disponibile[/yellow]")
            
            # Attendi prossimo controllo
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Monitoraggio interrotto[/bold]")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="BarberApp Auto-Booking Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python auto_book.py --service 10 --barber Giovanni
  python auto_book.py --service 10 --barber Giovanni --interval 60
  python auto_book.py --service 10 --barber Giovanni --min-hour 9 --max-hour 13
  python auto_book.py --service 10 --barber Giovanni --dry-run
        """
    )
    
    parser.add_argument(
        "--service", "-s",
        type=int,
        required=True,
        help="ID del servizio (es. 10 = taglio+barba)"
    )
    
    parser.add_argument(
        "--barber", "-b",
        type=str,
        required=True,
        help="Nome del barbiere (es. Giovanni)"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=300,
        help="Intervallo di controllo in secondi (default: 300 = 5 min)"
    )
    
    parser.add_argument(
        "--min-hour",
        type=int,
        default=None,
        help="Ora minima preferita (es. 9 = dalle 9:00)"
    )
    
    parser.add_argument(
        "--max-hour",
        type=int,
        default=None,
        help="Ora massima preferita (es. 13 = fino alle 13:00)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Trova slot ma non prenota effettivamente"
    )
    
    args = parser.parse_args()
    
    success = monitor_and_book(
        service_id=args.service,
        barber=args.barber,
        interval=args.interval,
        min_hour=args.min_hour,
        max_hour=args.max_hour,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

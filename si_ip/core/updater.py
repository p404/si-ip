import asyncio
from typing import Optional
from ..providers import get_provider
from ..resolvers.ip import IPResolver

class DNSUpdater:
   def __init__(self, config, logger):
       self.config = config
       self.logger = logger
       self.running = False
       
       Provider = get_provider(config['provider'])
       self.dns_provider = Provider(config, logger)
       self.ip_resolver = IPResolver()

   async def check_dependencies(self) -> bool:
       """Verify all required dependencies are working"""
       try:
           # Check IP resolver
           test_ip = await self.ip_resolver.get_ip()
           if not test_ip:
               self.logger.error('IP resolver check failed', extra={
                   'operation': 'dependency_check',
                   'component': 'ip_resolver'
               })
               return False

           self.logger.debug('IP resolver check successful', extra={
               'operation': 'dependency_check',
               'component': 'ip_resolver',
               'ip': test_ip
           })

           # Check DNS provider
           try:
               await self.dns_provider.record_exists(self.config['record_name'])
               self.logger.debug('DNS provider check successful', extra={
                   'operation': 'dependency_check',
                   'component': 'dns_provider'
               })
           except Exception as e:
               self.logger.debug('DNS provider check failed', extra={
                   'operation': 'dependency_check',
                   'component': 'dns_provider',
                   'error': str(e),
                   'error_type': type(e).__name__
               })
               return False

           return True

       except Exception as e:
           self.logger.error('Dependency check failed', extra={
               'operation': 'dependency_check',
               'error': str(e),
               'error_type': type(e).__name__
           })
           return False

   async def initialize_record(self) -> bool:
       """Create initial DNS record if it doesn't exist"""
       try:
           exists = await self.dns_provider.record_exists(self.config['record_name'])
           
           if not exists:
               self.logger.info('Creating initial DNS record', extra={
                   'record_name': self.config['record_name'],
                   'operation': 'record_init'
               })
               
               local_ip = await self.ip_resolver.get_ip()
               success = await self.dns_provider.create_record(
                   self.config['record_name'], 
                   local_ip
               )
               
               if not success:
                   self.logger.error('Failed to create initial record', extra={
                       'operation': 'record_init',
                       'record_name': self.config['record_name']
                   })
                   return False
                   
               self.logger.info('Initial DNS record created successfully', extra={
                   'record_name': self.config['record_name'],
                   'ip': local_ip,
                   'operation': 'record_init'
               })
           else:
               self.logger.debug('DNS record already exists', extra={
                   'record_name': self.config['record_name'],
                   'operation': 'record_init'
               })
               
           return True

       except Exception as e:
           self.logger.error('Error initializing record', extra={
               'error': str(e),
               'error_type': type(e).__name__,
               'operation': 'record_init',
               'record_name': self.config['record_name']
           })
           return False

   async def check_and_update(self) -> None:
       """Perform single check and update iteration"""
       try:
           local_ip = await self.ip_resolver.get_ip()
           self.logger.debug('Current IP fetched', extra={
               'ip': local_ip,
               'operation': 'ip_check'
           })

           current_ip = await self.dns_provider.get_record_ip(self.config['record_name'])
           self.logger.debug('DNS record IP fetched', extra={
               'ip': current_ip,
               'operation': 'dns_check'
           })
           
           if local_ip != current_ip:
               self.logger.info('IP change detected', extra={
                   'old_ip': current_ip,
                   'new_ip': local_ip,
                   'record_name': self.config['record_name'],
                   'operation': 'ip_change'
               })
               
               success = await self.dns_provider.update_record(
                   self.config['record_name'],
                   local_ip
               )
               
               if not success:
                   self.logger.error('Failed to update record', extra={
                       'operation': 'record_update',
                       'record_name': self.config['record_name'],
                       'old_ip': current_ip,
                       'new_ip': local_ip
                   })
           else:
               self.logger.debug('No IP change detected', extra={
                   'ip': local_ip,
                   'operation': 'ip_check'
               })
               self.logger.info(f"Record [{self.config['record_name']}.] are already up to date", extra={
                   'ip': local_ip,
                   'record_name': self.config['record_name'],
                   'operation': 'record_status'
               })

       except Exception as e:
           self.logger.error('Error in check and update', extra={
               'error': str(e),
               'error_type': type(e).__name__,
               'operation': 'update_check',
               'record_name': self.config['record_name']
           })
           raise

   async def run(self) -> None:
       """Main run loop"""
       try:
           # Initial checks
           if not await self.check_dependencies():
               raise RuntimeError("Dependency check failed")

           if not await self.initialize_record():
               raise RuntimeError("Record initialization failed")

           interval = float(self.config['refresh_interval'])
           self.logger.debug('Starting update loop', extra={
               'refresh_interval': interval,
               'operation': 'update_loop'
           })

           self.running = True
           while self.running:
               start_time = asyncio.get_event_loop().time()
               
               try:
                   await self.check_and_update()
               except Exception as e:
                   self.logger.error('Update iteration failed', extra={
                       'error': str(e),
                       'error_type': type(e).__name__,
                       'operation': 'update_iteration'
                   })

               # Calculate sleep time
               elapsed = asyncio.get_event_loop().time() - start_time
               sleep_time = max(0, interval - elapsed)
               
               self.logger.debug('Waiting for next check', extra={
                   'next_check_in': sleep_time,
                   'operation': 'sleep'
               })
               
               await asyncio.sleep(sleep_time)
               
       except Exception as e:
           self.logger.error('Fatal error in update loop', extra={
               'error': str(e),
               'error_type': type(e).__name__,
               'operation': 'update_loop',
               'record_name': self.config['record_name']
           })
           raise
       finally:
           self.running = False

   async def stop(self) -> None:
       """Gracefully stop the updater"""
       self.logger.info('Stopping updater', extra={'operation': 'shutdown'})
       self.running = False
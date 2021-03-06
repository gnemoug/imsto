# encoding: utf-8
"""
image.py

Created by liut on 2010-12-04.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

from _wand import *

class SimpImage(object):
	_max_width, _max_height = 0, 0

	"""docstring for ClassName"""
	def __init__(self, image = None):
		self._wand = NewMagickWand()
		if image is not None: self.read( image)

	def __del__(self):
		if self._wand:
			self._wand = DestroyMagickWand( self._wand )


	def __copy__( self ):
		c = Image()
		if self._wand:
			c._wand = CloneMagickWand( self._wand )
		return c


	def _clear( self ):
		ClearMagickWand( self._wand )


	def read( self, image):
		self._clear()

		if hasattr( image, 'read' ):
			c = image.read()
			MagickReadImageBlob( self._wand, c, len( c ) )
		else:
			MagickReadImage( self._wand, image )


	@property
	def format( self ):
		format = MagickGetImageFormat( self._wand )
		if format == '':
			return None
		else:
			return format

	@format.setter
	def format(self, value):
		'''The image format as a string, eg. "PNG".'''
		MagickSetImageFormat( self._wand, value )

	def max_height():
		doc = "The max_height property."
		def fget(self):
			return self._max_height
		def fset(self, value):
			self._max_height = value
		def fdel(self):
			del self._max_height
		return locals()
	max_height = property(**max_height())

	def max_width():
		doc = "The max_width property."
		def fget(self):
			#if self._max_width is None:
			#	self._max_width = 0
			return self._max_width
		def fset(self, value):
			self._max_width = value
		def fdel(self):
			del self._max_width
		return locals()
	max_width = property(**max_width())

	@property
	def quality(self):
		return MagickGetImageCompressionQuality( self._wand )

	@quality.setter
	def quality(self, value):
		MagickSetImageCompressionQuality( self._wand, int( round( value, 0 ) ) )

	def scale( self, size ):
		''' Scales the size of image to the given dimensions.
			size - A tuple containing the size of the scaled image.'''
		MagickScaleImage( self._wand, size[0], size[1] )

	def _get_size( self ):
		width = MagickGetImageWidth( self._wand )
		height = MagickGetImageHeight( self._wand )
		return ( width, height )
	size = property( _get_size, scale, None, 'A tuple containing the size of the image. Setting the size is the same as calling scale().' )

	def save( self, file = None ):
		''' Saves the image to a file.  If no file is specified, the file is
			saved with the original filename.'''
		if hasattr( file, 'write' ):
			size = size_t()
			b = MagickGetImageBlob( self._wand, size )
			try:
				file.write( ''.join( [chr( b[i] ) for i in range( 0, size.value + 1 )] ) )
			finally:
				MagickRelinquishMemory( b )
		else:
			MagickWriteImage( self._wand, file )


	def thumbnail( self, columns, rows = None, fit = True, max_width = 0, max_height = 0 ):
		if rows is None: rows = columns
		print "columns: {}, rows: {}, max_width: {}, max_height: {}".format(columns, rows, max_width, max_height)

		org_width, org_height = self.size

		if org_width <= columns and org_height <= rows:
			if MagickStripImage(self._wand):
				return True
			return False

		if fit:
			rel = float( org_width ) / float( org_height )
			if max_width > 0:
				columns = max_width
				rows = int( columns / rel )
			elif max_height > 0:
				rows = max_height
				columns = int( rows * rel )
			else:
				bounds = float( columns ) / float( rows )
				if rel >= bounds: rows = int( columns / rel )
				else: columns = int( rows * rel )
			print "columns: {}, rows: {}".format(columns, rows)
		return MagickThumbnailImage( self._wand, columns, rows )


	def cropThumbnail( self, dst_width, dst_height = None ):
		if dst_height is None: dst_height = dst_width

		org_width, org_height = self.size

		if org_width <= dst_width and org_height <= dst_height:
			if MagickStripImage(self._wand):
				return True
			return False

		ratio_x = float( dst_width ) / float( org_width );
		ratio_y = float( dst_height ) / float( org_height );

		if ratio_x > ratio_y:
			new_width  = int(dst_width)
			new_height = int(ratio_x * float( org_height ))
		else:
			new_height = int(dst_height)
			new_width  = int(ratio_y * float( org_width ))
		
		if not MagickThumbnailImage(self._wand, new_width, new_height):
			return False

		if new_width == dst_width and new_height == dst_height:
			return True

		crop_x = int((new_width - dst_width) / 2);
		crop_y = int((new_height - dst_height) / 2);

		print "crop_x: {0}, crop_y: {1}".format(crop_x, crop_y)

		if not MagickCropImage(self._wand, dst_width, dst_height, crop_x, crop_y):
			return False
		
		MagickSetImagePage(self._wand, dst_width, dst_height, 0, 0);
		return True



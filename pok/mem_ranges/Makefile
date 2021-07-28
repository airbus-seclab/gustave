all: bitmap unlink_bitmap
bitmap: bitmap.c
	@gcc $< -o $@ -lrt
unlink_bitmap: unlink_bitmap.c
	@gcc $< -o $@ -lrt
clean:
	@rm bitmap unlink_bitmap

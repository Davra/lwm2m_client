#ifndef TIME_OBJECT_H
#define TIME_OBJECT_H

#include <anjay/dm.h>

const anjay_dm_object_def_t **time_object_create(void);
void time_object_release(const anjay_dm_object_def_t **def);
void time_object_notify(anjay_t *anjay, const anjay_dm_object_def_t **def);
void time_object_send(anjay_t *anjay, const anjay_dm_object_def_t **def);

#endif // TIME_OBJECT_H

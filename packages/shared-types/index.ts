export type Role = 'Admin' | 'Viewer';
export type MediaType = 'movie' | 'tv' | 'anime';
export interface MediaRecord { id:string; media_type:MediaType; title:string; year?:number; size_bytes:number; sha256:string; resolution?:string; }
export interface ChunkRecord { part_number:number; channel:string; message_id:number; size_bytes:number; sha256:string; }
export interface Manifest { imdb_id?:string; tmdb_id?:string; title:string; year?:number; sha256:string; size:number; chunks:ChunkRecord[]; }
